"""
This module defines the Property class and property arithmetics.
"""

from dataclasses import dataclass
from typing import Type, Optional
from math import isclose

try:
    from typing import Self  # Python > 3.10 pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Self  # Python <= 3.10

from property_utils.units.descriptors import (
    MeasurementUnit,
    Dimension,
    CompositeDimension,
    UnitDescriptor,
)

# pylint: disable=unused-wildcard-import, wildcard-import
from property_utils.units.converters import *
from property_utils.units.units import NonDimensionalUnit
from property_utils.units.converter_types import UnitConverter, get_converter
from property_utils.exceptions.units.converter_types import UndefinedConverterError
from property_utils.exceptions.properties.property import (
    PropertyValidationError,
    PropertyUnitConversionError,
    PropertyBinaryOperationError,
    PropertyExponentError,
)
from property_utils.exceptions.units.converter_types import UnitConversionError
from property_utils.exceptions.base import PropertyUtilsException


def p(
    value: float, unit: UnitDescriptor = NonDimensionalUnit.NON_DIMENSIONAL
) -> "Property":
    """
    Create a property with a value and a unit.
    Default unit is non-dimensional, i.e. no unit.

    >>> from property_utils.units import KELVIN
    >>> p(350, KELVIN)
    <Property: 350 K>

    >>> p(20.23)
    <Property: 20.23 >
    """
    return Property(value, unit)


@dataclass
class Property:
    """
    A Property describes a value with a unit of measurement.

    A Property can have any 'value' or 'unit'; validations are not applied to it.
    For example, a Property with length units and negative value is valid.
    """

    value: float
    unit: UnitDescriptor
    unit_converter: Optional[Type[UnitConverter]] = None

    def __init__(self, value: float, unit: UnitDescriptor) -> None:
        if not isinstance(value, (float, int)):
            raise PropertyValidationError(
                f"cannot create Property; invalid 'value': {value}; expected numeric. "
            )
        if not isinstance(unit, (MeasurementUnit, Dimension, CompositeDimension)):
            raise PropertyValidationError(
                f"cannot create Property; invalid 'unit': {unit}. Expected an instance"
                " of one of: MeasurementUnit, Dimension, CompositeDimension. "
            )
        self.value = value
        self.unit = unit

    def eq(self, other: "Property", *, rel_tol=1e-9, abs_tol=0) -> bool:
        """
        Perform equality comparison between this and some other Property. This method
        of testing equality is preferable to the equality operator '==' because float
        point tolerance is taken into account.

        rel_tol is the maximum difference for being considered "close", relative
        to the magnitude of the input values.
        abs_tol is the maximum difference for being considered "close", regardless of
        the magnitude of the input values.
        For the values to be considered close, the difference between them must be
        smaller than at least one of the tolerances.

        Raises `PropertyBinaryOperationError` if an error occurs during conversion
        of other's units.

        >>> from property_utils.units.units import AbsoluteTemperatureUnit, LengthUnit
        >>> T1 = Property(33.333333, AbsoluteTemperatureUnit.KELVIN)
        >>> T2 = Property(100/3, AbsoluteTemperatureUnit.KELVIN)
        >>> T1 == T2
        False
        >>> T1.eq(T2)
        False
        >>> T1.eq(T2, rel_tol=0.1)
        True
        """
        if not isinstance(other, Property):
            return False
        if not self.unit.isinstance(other.unit.to_generic()):
            return False
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUtilsException as exc:
            raise PropertyBinaryOperationError(
                f"during conversion of {other} to ({self.unit}) units an error occured: ",
                exc,
            ) from None
        return isclose(self.value, prop.value, rel_tol=rel_tol, abs_tol=abs_tol)

    def to_si(self) -> Self:
        """
        Create a new property with SI units.

        Raises `ImpossiblePropertyUnitConverion` if there is no converter registered
        for the unit.

        Raises `InvalidUnitConversion` if any error occurs in the unit conversion.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T.to_si()
        <Property: 373.15 K>
        """
        if isinstance(self.unit, MeasurementUnit):
            return self.to_unit(self.unit.si())
        if isinstance(self.unit, Dimension):
            return self.to_unit(self.unit.unit.si() ** self.unit.power)
        if isinstance(self.unit, CompositeDimension):
            return self.to_unit(self.unit.to_generic().to_si())
        raise PropertyValidationError(
            f"cannot convert Property to SI; 'unit' is invalid: {self.unit}. "
        )

    def to_unit(self, unit: UnitDescriptor) -> Self:
        """
        Create a new property with specified unit.

        Raises `PropertyUnitConversionError` if the unit is not of the same type.

        Raises `ImpossiblePropertyUnitConverion` if there is no converter registered
        for the unit.

        Raises `UnitConversionError` if any error occurs in the unit conversion.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T.to_unit(RelativeTemperatureUnit.FAHRENHEIT)
        <Property: 212.0 °F>
        """
        if not unit.isinstance(self.unit.to_generic()):
            raise PropertyUnitConversionError(
                f"cannot convert {self} to ({unit}) units; 'unit' should be an instance"
                f" of {self.unit.to_generic()}. "
            )
        try:
            converter = self._converter()
        except UndefinedConverterError:
            raise PropertyUnitConversionError(
                f"cannot convert property {self} to units: {unit}; no unit converter "
                f" found for {unit.to_generic()}. "
                "Did you forget to @register_converter? "
            ) from None
        try:
            value = converter.convert(self.value, self.unit, unit)
        except UnitConversionError as exc:
            raise exc from None
        return self.__class__(value=value, unit=unit)

    def __neg__(self) -> Self:
        """
        Defines negation of properties.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T = Property(3, RelativeTemperatureUnit.CELCIUS)
        >>> -T
        <Property: -3 °C>
        """
        return self.__class__(-self.value, self.unit)

    def __mul__(self, other) -> "Property":
        """
        Defines multiplication between properties and numerics.

        >>> from property_utils.units.units import AbsoluteTemperatureUnit, LengthUnit
        >>> T = Property(300, AbsoluteTemperatureUnit.KELVIN)
        >>> 2*T
        <Property: 600 K>
        >>> A = Property(10, LengthUnit.METER**2)
        >>> T * A
        <Property: 3000 (m^2) * K>
        """
        if isinstance(other, (float, int)):
            return Property(self.value * other, self.unit)
        if isinstance(other, Property):
            return Property(
                self.value * other.value, (self.unit * other.unit).simplified()
            )
        raise PropertyBinaryOperationError(
            f"cannot multiply {self} with {other}; "
            "second operand must be numeric or Property. "
        )

    def __rmul__(self, other) -> "Property":
        """
        Defines multiplication between properties and numerics.

        >>> from property_utils.units.units import AbsoluteTemperatureUnit, LengthUnit
        >>> T = Property(300, AbsoluteTemperatureUnit.KELVIN)
        >>> 2*T
        <Property: 600 K>
        >>> A = Property(10, LengthUnit.METER**2)
        >>> T * A
        <Property: 3000 (m^2) * K>
        """
        return self.__mul__(other)

    def __truediv__(self, other) -> "Property":
        """
        Defines division between properties and numerics.

        >>> from property_utils.units.units import AbsoluteTemperatureUnit, LengthUnit
        >>> T = Property(500, AbsoluteTemperatureUnit.KELVIN)
        >>> T/2
        <Property: 250.0 K>
        >>> A = Property(10, LengthUnit.METER**2)
        >>> T / A
        <Property: 50.0 K / (m^2)>
        """
        if isinstance(other, (float, int)):
            try:
                value = self.value / other
            except ZeroDivisionError:
                raise PropertyBinaryOperationError(
                    f"cannot divide {self} with {other}; denominator is zero. "
                ) from None
            return Property(value, self.unit)
        if isinstance(other, Property):
            try:
                value = self.value / other.value
            except ZeroDivisionError:
                raise PropertyBinaryOperationError(
                    f"cannot divide {self} with {other}; denominator's value is zero. "
                ) from None
            return Property(value, (self.unit / other.unit).simplified())
        raise PropertyBinaryOperationError(
            f"cannot divide {self} with {other}; "
            "denominator must be numeric or Property. "
        )

    def __rtruediv__(self, other) -> "Property":
        """
        Defines right division between properties and numerics.

        >>> from property_utils.units.units import AbsoluteTemperatureUnit
        >>> T = Property(500, AbsoluteTemperatureUnit.KELVIN)
        >>> 100/T
        <Property: 0.2  / K>
        """
        if isinstance(other, (float, int)):
            try:
                value = other / self.value
            except ZeroDivisionError:
                raise PropertyBinaryOperationError(
                    f"cannot divide {self} with {other}; denominator is zero. "
                ) from None
            return Property(value, self.unit.inverse())
        if isinstance(other, Property):
            try:
                value = other.value / self.value
            except ZeroDivisionError:
                raise PropertyBinaryOperationError(
                    f"cannot divide {self} with {other}; denominator's value is zero. "
                ) from None
            return Property(value, (other.unit / self.unit).simplified())
        raise PropertyBinaryOperationError(
            f"cannot divide {self} with {other}; "
            "numerator must be numeric or Property. "
        )

    def __add__(self, other) -> Self:
        """
        Defines addition between properties.

        >>> from property_utils.units.units import LengthUnit
        >>> x1 = Property(15, LengthUnit.METER)
        >>> x2 = Property(5, LengthUnit.METER)
        >>> x1 + x2
        <Property: 20 m>
        """
        if not isinstance(other, self.__class__):
            raise PropertyBinaryOperationError(
                f"cannot add {other} to ({self}); {other} is not a {self.__class__}; "
                "only same properties can be added to each other. "
            )
        if not self.unit.isinstance(other.unit.to_generic()):
            raise PropertyBinaryOperationError(
                f"cannot add ({other}) to ({self}); "
                f"({other}) must have ({self.unit.to_generic()}) units. "
            )
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot add ({other}) to ({self}); ({other}) does not have the same "
                f"units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot add ({other}) to ({self});", exc
            ) from None
        return self.__class__(self.value + prop.value, self.unit)

    def __radd__(self, other) -> Self:
        """
        Defines right addition between properties.

        >>> from property_utils.units.units import LengthUnit
        >>> x1 = Property(15, LengthUnit.METER)
        >>> x2 = Property(5, LengthUnit.METER)
        >>> x1 + x2
        <Property: 20 m>
        """
        return self.__add__(other)

    def __sub__(self, other) -> Self:
        """
        Defines subtraction between properties.

        >>> from property_utils.units.units import TimeUnit
        >>> t1 = Property(2, TimeUnit.MINUTE)
        >>> t2 = Property(60, TimeUnit.SECOND)
        >>> t1 - t2
        <Property: 1.0 min>
        """
        if not isinstance(other, self.__class__):
            raise PropertyBinaryOperationError(
                f"cannot subtract {other} from ({self}); {other} is not a "
                f"{self.__class__}; only same properties can be subtracted from each "
                "other. "
            )
        if not self.unit.isinstance(other.unit.to_generic()):
            raise PropertyBinaryOperationError(
                f"cannot subtract ({other}) from ({self}); "
                f"({other}) must have ({self.unit.to_generic()}) units. "
            )
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot subtract ({other}) from ({self}); ({other}) does not have the "
                f"same units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot subtract ({other}) from ({self});", exc
            ) from None
        return self.__class__(self.value - prop.value, self.unit)

    def __rsub__(self, other) -> Self:
        """
        Defines right subtraction between properties.

        >>> from property_utils.units.units import TimeUnit
        >>> t1 = Property(2, TimeUnit.MINUTE)
        >>> t2 = Property(60, TimeUnit.SECOND)
        >>> t1 - t2
        <Property: 1.0 min>
        """
        if not isinstance(other, self.__class__):
            raise PropertyBinaryOperationError(
                f"cannot subtract {self} from ({other}); {other} is not a "
                f"{self.__class__}; only same properties can be subtracted from each "
                "other. "
            )
        if not self.unit.isinstance(other.unit.to_generic()):
            raise PropertyBinaryOperationError(
                f"cannot subtract ({self}) from ({other}); "
                f"({other}) must have ({self.unit.to_generic()}) units. "
            )
        return other.__add__(-self)

    def __pow__(self, power) -> "Property":
        """
        Defines exponentiation for properties.

        >>> from property_utils.units.units import LengthUnit
        >>> L = Property(5, LengthUnit.METER)
        >>> L**3
        <Property: 125 (m^3)>
        """
        if not isinstance(power, (float, int)):
            raise PropertyExponentError(
                f"invalid exponent: {power}; expected numeric. "
            )
        return Property(self.value**power, self.unit**power)

    def __eq__(self, other) -> bool:
        """
        Defines equality between properties.
        Prefer Property.eq instead.The equality operator returns False even for very
        small differences between floating point values.

        >>> from property_utils.units.units import LengthUnit
        >>> L1 = Property(500, LengthUnit.CENTI_METER)
        >>> L2 = Property(5, LengthUnit.METER)
        >>> L1 == L2
        True

        >>> L3 = Property(6, LengthUnit.METER)
        >>> L2 == L3
        False
        """
        if not isinstance(other, Property):
            return False
        if not self.unit.isinstance(other.unit.to_generic()):
            return False
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUtilsException as exc:
            raise PropertyBinaryOperationError(
                f"during conversion of {other} to ({self.unit}) units an error occured: ",
                exc,
            ) from None
        return self.value == prop.value

    def __ne__(self, other) -> bool:
        """
        Defines inequality between properties.
        Prefer Property.eq instead.The inequality operator returns True even for very
        small differences between floating point values.

        >>> from property_utils.units.units import LengthUnit
        >>> L1 = Property(500, LengthUnit.CENTI_METER)
        >>> L2 = Property(5, LengthUnit.METER)
        >>> L1 != L2
        False

        >>> L3 = Property(6, LengthUnit.METER)
        >>> L2 != L3
        True
        """
        return not self.__eq__(other)

    def __gt__(self, other) -> bool:
        """
        Defines comparison between properties.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T1 = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T2 = Property(213, RelativeTemperatureUnit.FAHRENHEIT)
        >>> T1 > T2
        False
        """
        self._validate_comparison_input(other)
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self}); ({other}) does not have the "
                f"same units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self});", exc
            ) from None
        return self.value > prop.value

    def __ge__(self, other) -> bool:
        """
        Defines comparison between properties.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T1 = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T2 = Property(212, RelativeTemperatureUnit.FAHRENHEIT)
        >>> T1 >= T2
        True
        """
        self._validate_comparison_input(other)
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self}); ({other}) does not have the "
                f"same units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self});", exc
            ) from None
        return self.value >= prop.value

    def __lt__(self, other) -> bool:
        """
        Defines comparison between properties.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T1 = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T2 = Property(213, RelativeTemperatureUnit.FAHRENHEIT)
        >>> T1 < T2
        True
        """
        self._validate_comparison_input(other)
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self}); ({other}) does not have the "
                f"same units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self});", exc
            ) from None
        return self.value < prop.value

    def __le__(self, other) -> bool:
        """
        Defines comparison between properties.

        >>> from property_utils.units.units import RelativeTemperatureUnit
        >>> T1 = Property(100, RelativeTemperatureUnit.CELCIUS)
        >>> T2 = Property(213, RelativeTemperatureUnit.FAHRENHEIT)
        >>> T1 <= T2
        True
        """
        self._validate_comparison_input(other)
        try:
            prop = other.to_unit(self.unit) if self.unit != other.unit else other
        except PropertyUnitConversionError:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self}); ({other}) does not have the "
                f"same units as ({self}) and there is no unit converter registered for "
                f"({self.unit.to_generic()}). "
            ) from None
        except UnitConversionError as exc:
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self});", exc
            ) from None
        return self.value <= prop.value

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    def __repr__(self) -> str:
        return f"<Property: {str(self)}>"

    def _converter(self) -> Type[UnitConverter]:
        """
        Raises `UndefinedConverter` if a converter is not defined.
        """
        if self.unit_converter is None:
            self.unit_converter = self._get_converter()
        return self.unit_converter

    def _get_converter(self) -> Type[UnitConverter]:
        """
        Raises `UndefinedConverter` if a converter is not defined.
        """
        return get_converter(self.unit.to_generic())

    def _validate_comparison_input(self, other) -> None:
        """
        Raises `PropertyBinaryOperationError` if other is not a Property or if it does
        not have the same unit type as this Property.
        """
        if not isinstance(other, Property):
            raise PropertyBinaryOperationError(
                f"cannot compare {other} to ({self}); {other} is not a Property; "
                "only properties can be compared to properties. "
            )
        if not self.unit.isinstance(other.unit.to_generic()):
            raise PropertyBinaryOperationError(
                f"cannot compare ({other}) to ({self}); "
                f"({other}) must have ({self.unit.to_generic()}) units. "
            )
