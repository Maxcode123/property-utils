"""
This module includes definitions for generic unit descriptors and unit descriptors.

A unit descriptor is an interface that describes a measurement unit. It can represent
anything like °C, m^3, mol/m^3/s etc.

A generic unit descriptor is an interface that describes a generic measurement unit. It
can represent e.g. a temperature unit, a volume unit, a reaction rate unit etc.
"""

from enum import Enum, EnumMeta
from typing import List, Union, Protocol, Optional, TypeVar, Dict
from collections import Counter
from dataclasses import dataclass, field, replace

try:
    from typing import TypeAlias  # Python >= 3.10 pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import TypeAlias  # Python < 3.10


from property_utils.exceptions.units.descriptors import (
    DescriptorBinaryOperationError,
    DescriptorExponentError,
    UnitDescriptorTypeError,
)


class GenericUnitDescriptor(Protocol):
    """
    Descriptor for a property unit that does not have a specific unit.

    e.g. a  generic descriptor can represent a Temperature unit that does not have a
    specific value like Celcius or Fahrenheit.
    """

    def to_si(self) -> "UnitDescriptor":
        """
        Create a unit descriptor with SI units.
        """

    def inverse_generic(self) -> "GenericCompositeDimension":
        """
        Create a generic composite with inverse units.
        """

    def is_equivalent(self, other: "GenericUnitDescriptor") -> bool:
        """
        Returns True if this generic is equivalent to the given one, False otherwise.

        A generic can be equivalent with another generic if the latter or the former
        is an alias.
        """

    def __mul__(
        self, generic: "GenericUnitDescriptor"
    ) -> "GenericCompositeDimension": ...

    def __truediv__(
        self, generic: "GenericUnitDescriptor"
    ) -> "GenericCompositeDimension": ...

    def __pow__(self, power: float) -> "GenericUnitDescriptor": ...

    def __eq__(self, generic) -> bool: ...

    def __hash__(self) -> int: ...

    def __str__(self) -> str: ...


class UnitDescriptor(Protocol):
    """
    Descriptor for a property unit that has a specific unit, e.g. cm^2 or ft^2.
    """

    def si(self) -> "UnitDescriptor":
        """
        Returns this descriptor with SI units.
        """

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance of the generic, False
        otherwise.

        A unit descriptor is an instance of a generic if the generic of the unit
        descriptor is equal to the generic.

        Equality between generics is checked with the `==` operator.
        """

    def isinstance_equivalent(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance-equivalent of the generic,
        False otherwise.

        A unit descriptor is an instance-equivalent of a generic if the generic of the
        unit descriptor is equivalent to the generic.

        Equivalence between generics is checked with the `is_equivalent` method.
        """

    def to_generic(self) -> GenericUnitDescriptor:
        """
        Create a generic descriptor from this UnitDescriptor.
        """

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.
        """

    def __mul__(self, descriptor: "UnitDescriptor") -> "CompositeDimension": ...

    def __truediv__(self, descriptor: "UnitDescriptor") -> "CompositeDimension": ...

    def __pow__(self, power: float) -> "UnitDescriptor": ...

    def __hash__(self) -> int: ...

    def __str__(self) -> str: ...


Descriptor: TypeAlias = Union[GenericUnitDescriptor, UnitDescriptor]


class MeasurementUnitMeta(EnumMeta):
    """
    Metaclass for MeasurementUnit. Defines multiplication, division and exponent
    operations for MeasurementUnit class (and subclasses). These operations produce
    GenericUnitDescriptor(s).
    """

    def to_si(cls) -> "MeasurementUnit":
        """
        Create a MeasurementUnit with SI units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            ...     KELVIN = "K"
            ...     @classmethod
            ...     def si(cls):
            ...         return cls.KELVIN
            >>> TemperatureUnit.to_si()
            <TemperatureUnit: K>
        """
        if hasattr(cls, "si"):
            return cls.si()
        raise NotImplementedError

    def inverse_generic(cls) -> "GenericCompositeDimension":
        """
        Create a generic composite with inverse units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> TemperatureUnit.inverse_generic()
            <GenericCompositeDimension:  / TemperatureUnit>
        """
        return GenericCompositeDimension([], [GenericDimension(cls)])

    # pylint: disable=too-many-return-statements
    def is_equivalent(cls, other: GenericUnitDescriptor) -> bool:
        """
        Returns True if this generic is equivalent to the given one, False otherwise.

        A generic can be equivalent with another generic if the latter or the former
        is an alias.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class MassUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> class ForceUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return MassUnit * LengthUnit / (TimeUnit**2)

            >>> ForceUnit.is_equivalent(MassUnit * LengthUnit / (TimeUnit**2))
            True

            >>> class EnergyUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return ForceUnit * LengthUnit

            >>> EnergyUnit.is_equivalent(MassUnit * (LengthUnit**2) / (TimeUnit**2))
            True
        """
        if isinstance(other, MeasurementUnitType):
            return cls == other

        if isinstance(other, GenericDimension):
            if cls == other.unit_type and other.power == 1:
                return True

            if issubclass(other.unit_type, AliasMeasurementUnit):
                return (
                    other.unit_type.aliased_generic_descriptor() ** other.power
                ).is_equivalent(cls)

            if issubclass(cls, AliasMeasurementUnit):
                return cls.aliased_generic_descriptor().is_equivalent(other)

        elif isinstance(other, GenericCompositeDimension):
            if (
                other.denominator == []
                and len(other.numerator) == 1
                and other.numerator[0].is_equivalent(cls)
            ):
                return True

            if issubclass(cls, AliasMeasurementUnit):
                return cls.aliased_generic_descriptor().is_equivalent(other)

        return False

    def __mul__(cls, other: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between MeasurementUnit types and other generic
        descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> TemperatureUnit * TimeUnit
            <GenericCompositeDimension: TemperatureUnit * TimeUnit>
        """
        if isinstance(other, GenericCompositeDimension):
            numerator = other.numerator.copy()
            denominator = other.denominator.copy()
            numerator.append(GenericDimension(cls))
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(other, GenericDimension):
            return GenericCompositeDimension(numerator=[GenericDimension(cls), other])
        if isinstance(other, MeasurementUnitType):
            return GenericCompositeDimension(
                numerator=[
                    GenericDimension(cls),
                    GenericDimension(other),
                ]
            )
        raise DescriptorBinaryOperationError(f"cannot multiply {cls} with {other}. ")

    def __truediv__(cls, other: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines division between MeasurementUnit types and other generic
        descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> TemperatureUnit / TimeUnit
            <GenericCompositeDimension: TemperatureUnit / TimeUnit>
        """
        if isinstance(other, GenericCompositeDimension):
            numerator = other.denominator.copy()
            denominator = other.numerator.copy()
            numerator.append(GenericDimension(cls))
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(other, GenericDimension):
            return GenericCompositeDimension(
                numerator=[GenericDimension(cls)], denominator=[other]
            )
        if isinstance(other, MeasurementUnitType):
            return GenericCompositeDimension(
                numerator=[GenericDimension(cls)],
                denominator=[GenericDimension(other)],
            )
        raise DescriptorBinaryOperationError(f"cannot divide {cls} with {other}. ")

    def __pow__(cls, power: float) -> "GenericDimension":
        """
        Defines exponentiation of MeasurementUnit types.

        Examples:
            >>> class TimeUnit(MeasurementUnit): ...
            >>> TimeUnit**3
            <GenericDimension: TimeUnit^3>
        """
        return GenericDimension(cls, power)

    def __str__(cls) -> str:
        return cls.__name__

    def __repr__(cls) -> str:
        return f"<MeasurementUnit: {str(cls)}>"


class MeasurementUnit(Enum, metaclass=MeasurementUnitMeta):
    """
    Base class for all measurement units of physical quantities.

    Each measurement-unit class is an enumeration of the available units for a
    quantity.

    Subclasses should only enumerate measurement units of primitive physical
    quantities, i.e. units that cannot be produced from other units.
    e.g. length is an acceptable quantity, but volume is not because its' units are
    produced from length units.

    Examples:
        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        ...     KELVIN = "K"
        ...     RANKINE = "R"
        ...     FAHRENHEIT = "F"
    """

    @classmethod
    def si(cls) -> "MeasurementUnit":
        """
        Returns the SI unit of this measurement unit.
        """
        raise NotImplementedError

    @classmethod
    def is_non_dimensional(cls) -> bool:
        """
        Implement this function for defined measurement units that are non dimensional.

        Examples:
            >>> class NonDimensionalUnit(MeasurementUnit):
            ...     NON_DIMENSIONAL = ""
            ...     @classmethod
            ...     def is_non_dimensional(cls) -> bool: return True

            >>> NonDimensionalUnit.is_non_dimensional()
            True
        """
        return False

    @staticmethod
    def from_descriptor(descriptor: UnitDescriptor) -> "MeasurementUnit":
        """
        Create a MeasurementUnit from given descriptor.
        If descriptor is already a MeasurementUnit, it returns the same object.

        This function does not serve as a constructor for MeasurementUnit, rather it
        is intended to be used to convert an unknown unit descriptor to a
        MeasurementUnit.

        Raises `UnitDescriptorTypeError` if given descriptor cannot be translated
        to a MeasurementUnit instance.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"

            >>> celcius = MeasurementUnit.from_descriptor(TemperatureUnit.CELCIUS**2)
            >>> celcius
            <TemperatureUnit: C>
        """
        if isinstance(descriptor, Dimension):
            return descriptor.unit
        if isinstance(descriptor, MeasurementUnit):
            return descriptor
        raise UnitDescriptorTypeError(
            f"cannot create MeasurementUnit from descriptor: {descriptor}"
        )

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the MeasurementUnit is an instance of the generic, False
        otherwise.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"

            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> TemperatureUnit.CELCIUS.isinstance(TemperatureUnit)
            True

            >>> TemperatureUnit.CELCIUS.isinstance(LengthUnit)
            False
        """
        return type(self) == generic  # pylint: disable=unidiomatic-typecheck

    def isinstance_equivalent(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance-equivalent of the generic,
        False otherwise.

        A unit descriptor is an instance-equivalent of a generic if the generic of the
        unit descriptor is equivalent to the generic.

        Equivalence between generics is checked with the `is_equivalent` method.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class AreaUnit(AliasMeasurementUnit):
            ...     HECTARE = "ha"
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls): return LengthUnit**2

            >>> AreaUnit.HECTARE.isinstance_equivalent(AreaUnit)
            True
            >>> AreaUnit.HECTARE.isinstance_equivalent(LengthUnit**2)
            True
        """
        return self.to_generic().is_equivalent(generic)

    def to_generic(self) -> GenericUnitDescriptor:
        """
        Create a generic descriptor from this MeasurementUnit.

        Examples:
            >>> class AmountUnit(MeasurementUnit):
            ...     MOL = "mol"

            >>> AmountUnit.MOL.to_generic()
            <MeasurementUnit: AmountUnit>
        """
        return self.__class__

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"
            >>> TemperatureUnit.KELVIN.inverse()
            <CompositeDimension:  / K>
        """
        return CompositeDimension([], [Dimension(self)])

    def __mul__(self, descriptor: UnitDescriptor) -> "CompositeDimension":
        """
        Defines multiplication between MeasurementUnit objects and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     FAHRENHEIT = "F"
            >>> class TimeUnit(MeasurementUnit):
            ...     HOUR = "hr"
            >>> TemperatureUnit.FAHRENHEIT * TimeUnit.HOUR
            <CompositeDimension: F * hr>
        """
        if isinstance(descriptor, MeasurementUnit):
            return Dimension(self) * Dimension(descriptor)
        if isinstance(descriptor, (Dimension, CompositeDimension)):
            return Dimension(self) * descriptor
        raise DescriptorBinaryOperationError(
            f"cannot multiply {self} with {descriptor}. "
        )

    def __truediv__(self, descriptor: UnitDescriptor) -> "CompositeDimension":
        """
        Defines division between MeasurementUnit objects and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     FAHRENHEIT = "F"
            >>> class TimeUnit(MeasurementUnit):
            ...     HOUR = "hr"
            >>> TemperatureUnit.FAHRENHEIT / TimeUnit.HOUR
            <CompositeDimension: F / hr>
        """
        if isinstance(descriptor, MeasurementUnit):
            return Dimension(self) / Dimension(descriptor)
        if isinstance(descriptor, (Dimension, CompositeDimension)):
            return Dimension(self) / descriptor
        raise DescriptorBinaryOperationError(
            f"cannot divide {self} with {descriptor}. "
        )

    def __pow__(self, power: float) -> "Dimension":
        """
        Defines exponentiation of MeasurementUnit objects.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     FEET = "ft"
            >>> LengthUnit.FEET**3
            <Dimension: ft^3>
        """
        # always keep non dimensional units to the first power
        power = 1 if self.is_non_dimensional() else power

        return Dimension(self, power)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {str(self)}>"

    def __str__(self) -> str:
        return self.value


# mypy does treat Type[MeasurementUnit] and MeasurementUnitMeta as equals.
# use MeasurementUnitType instead of Type[MeasurementUnit].
MeasurementUnitType: TypeAlias = MeasurementUnitMeta


class AliasMeasurementUnit(MeasurementUnit):
    """
    Base class for common composite units of physical quantities.

    Subclasses of `MeasurementUnit` represent only primitive physical quantities.
    However, many common physical properties have composite units (e.g. pressure, force,
    energy, etc), thus subclasses of this class alias composite units as primitive ones.

    Only very common composite units should be aliased.

    e.g. you can create an alias for pressure units, instead of using mass * length / (
        time^2) units.

    Examples:
        >>> class PressureUnit(AliasMeasurementUnit):
        ...     BAR = "bar"
        ...     PASCAL = "Pa"
        ...     KILO_PASCAL = "kPa"
        ...     PSI = "psi"
    """

    @staticmethod
    def from_descriptor(descriptor: UnitDescriptor) -> MeasurementUnit:
        """
        Create an AliasMeasurementUnit from given descriptor.
        If descriptor is already an AliasMeasurementUnit, it returns the same object.

        This function does not serve as a constructor for AliasMeasurementUnit, rather
        it is intended to be used to convert an unknown unit descriptor to an
        AliasMeasurementUnit.

        Subclasses should implement aliased_generic_descriptor and alias_mapping
        methods.

        Raises `UnitDescriptorTypeError` if given descriptor cannot be translated
        to an AliasMeasurementUnit  instance.

        Examples:
            >>> class PressureUnit(AliasMeasurementUnit):
            ...     BAR = "bar"

            >>> bar = MeasurementUnit.from_descriptor(PressureUnit.BAR**(-1))
            >>> bar
            <PressureUnit: bar>
        """
        if isinstance(descriptor, Dimension) and isinstance(
            descriptor.unit, AliasMeasurementUnit
        ):
            return descriptor.unit
        if isinstance(descriptor, AliasMeasurementUnit):
            return descriptor
        raise UnitDescriptorTypeError(
            f"cannot create AliasMeasurementUnit from descriptor {descriptor}"
        )

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericUnitDescriptor:
        """
        Implement this method by returning the generic of the unit descriptor that this
        measurement unit aliases.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class AreaUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return LengthUnit**2
        """
        raise NotImplementedError


@dataclass
class GenericDimension:
    """
    Represents a generic property unit or a generic property unit to some power.

    e.g. a generic dimension can be a temperature dimension or a volume dimension
    (length dimension to the 3rd power).

    Examples:
        >>> class MassUnit(MeasurementUnit): ...
        >>> MassUnit**2
        <GenericDimension: MassUnit^2>
    """

    unit_type: MeasurementUnitType
    power: float = 1

    def __init__(self, unit_type: MeasurementUnitType, power: float = 1) -> None:
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        self.unit_type = unit_type
        self.power = power

    def to_si(self) -> "Dimension":
        """
        Create a Dimension with SI units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            ...     KELVIN = "K"
            ...     @classmethod
            ...     def si(cls): return cls.KELVIN
            >>> (TemperatureUnit**2).to_si()
            <Dimension: K^2>
        """
        return Dimension(self.unit_type.to_si(), self.power)

    def inverse_generic(self) -> "GenericCompositeDimension":
        """
        Create a generic composite with inverse units.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> (LengthUnit**2).inverse_generic()
            <GenericCompositeDimension:  / (LengthUnit^2)>
        """
        return GenericCompositeDimension([], [replace(self)])

    # pylint: disable=too-many-return-statements
    def is_equivalent(self, other: GenericUnitDescriptor) -> bool:
        """
        Returns True if this generic is equivalent to the given one, False otherwise.

        A generic can be equivalent with another generic if the latter or the former
        is an alias.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class MassUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> class ForceUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return MassUnit * LengthUnit / (TimeUnit**2)

            >>> ForceUnit.is_equivalent(MassUnit * LengthUnit / (TimeUnit**2))
            True

            >>> class EnergyUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return ForceUnit * LengthUnit

            >>> EnergyUnit.is_equivalent(MassUnit * (LengthUnit**2) / (TimeUnit**2))
            True
        """
        if isinstance(other, MeasurementUnitType):
            if self.unit_type == other and self.power == 1:
                return True

            if issubclass(other, AliasMeasurementUnit):
                return other.aliased_generic_descriptor().is_equivalent(self)  # type: ignore[attr-defined]

        elif isinstance(other, GenericDimension):
            if self.unit_type == other.unit_type and self.power == other.power:
                return True

            if issubclass(other.unit_type, AliasMeasurementUnit):
                return (
                    other.unit_type.aliased_generic_descriptor() ** other.power
                ).is_equivalent(self)

            if issubclass(self.unit_type, AliasMeasurementUnit):
                return (
                    self.unit_type.aliased_generic_descriptor() ** self.power
                ).is_equivalent(other)

        elif isinstance(other, GenericCompositeDimension):
            if (
                other.denominator == []
                and len(other.numerator) == 1
                and other.numerator[0].is_equivalent(self)
            ):
                return True

            if issubclass(self.unit_type, AliasMeasurementUnit):
                return (
                    self.unit_type.aliased_generic_descriptor() ** self.power
                ).is_equivalent(other)

        return False

    def __mul__(self, generic: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between GenericDimension(s) and other generic
        descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> (TemperatureUnit**2) * TimeUnit
            <GenericCompositeDimension: (TemperatureUnit^2) * TimeUnit>
        """
        if isinstance(generic, GenericCompositeDimension):
            numerator = generic.numerator.copy()
            denominator = generic.denominator.copy()
            numerator.append(self)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(generic, GenericDimension):
            return GenericCompositeDimension(numerator=[self, generic])
        if isinstance(generic, MeasurementUnitType):
            return GenericCompositeDimension(
                numerator=[self, GenericDimension(generic)]
            )
        raise DescriptorBinaryOperationError(f"cannot multiply {self} with {generic}. ")

    def __truediv__(
        self, generic: GenericUnitDescriptor
    ) -> "GenericCompositeDimension":
        """
        Defines division between GenericDimension(s) and other generic descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> TemperatureUnit / (TimeUnit**2)
            <GenericCompositeDimension: TemperatureUnit / (TimeUnit^2)>
        """
        if isinstance(generic, GenericCompositeDimension):
            numerator = generic.denominator.copy()
            denominator = generic.numerator.copy()
            numerator.append(self)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(generic, GenericDimension):
            return GenericCompositeDimension(numerator=[self], denominator=[generic])
        if isinstance(generic, MeasurementUnitType):
            return GenericCompositeDimension(
                numerator=[self], denominator=[GenericDimension(generic)]
            )
        raise DescriptorBinaryOperationError(f"cannot divide {self} with {generic}. ")

    def __pow__(self, power: float) -> "GenericDimension":
        """
        Defines exponentiation of GenericDimension.

        Examples:
            >>> class TimeUnit(MeasurementUnit): ...
            >>> (TimeUnit**2)**3
            <GenericDimension: TimeUnit^6>
        """
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        self.power *= power
        return self

    def __eq__(self, generic) -> bool:
        """
        Defines equality for GenericDimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> (TemperatureUnit**2) != TemperatureUnit
            True
        """
        if not isinstance(generic, GenericDimension):
            return False
        return self.unit_type == generic.unit_type and self.power == generic.power

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        s = self.unit_type.__name__
        if self.power != 1:
            return f"({s}^{self.power})"
        return s

    def __repr__(self) -> str:
        if self.power != 1:
            return f"<GenericDimension: {self.unit_type.__name__}^{self.power}>"
        return f"<GenericDimension: {self.unit_type.__name__}>"


@dataclass
class Dimension:
    """
    A Dimension is a wrapper around MeasurementUnit.

    Objects of this class can represent either a simple MeasurementUnit or a
    MeasurementUnit to some power.

    Examples:
        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"

        >>> TimeUnit.SECOND**2
        <Dimension: s^2>
    """

    unit: MeasurementUnit
    power: float = 1

    def __init__(self, unit: MeasurementUnit, power: float = 1) -> None:
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        self.unit = unit
        self.power = power

    @staticmethod
    def from_descriptor(descriptor: UnitDescriptor) -> "Dimension":
        """
        Create a Dimension from given descriptor.
        If descriptor is already a Dimension, it returns the same object.

        This function does not serve as a constructor for Dimension, rather it
        is intended to be used to convert an unknown unit descriptor to a Dimension.

        Raises `UnitDescriptorTypeError` if given descriptor cannot be translated
        to a Dimension instance.
        """
        if isinstance(descriptor, Dimension):
            return descriptor
        if isinstance(descriptor, MeasurementUnit):
            return Dimension(descriptor)
        raise UnitDescriptorTypeError(
            f"cannot create Dimension from descriptor: {descriptor}"
        )

    def si(self) -> "Dimension":
        """
        Returns this dimension in SI units.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            ...     FOOT = "ft"
            ...     @classmethod
            ...     def si(cls): return cls.METER

            >>> (LengthUnit.FOOT**2).si()
            <Dimension: m^2>
        """
        return Dimension(self.unit.si(), self.power)

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the Dimension is an instance of the generic, False
        otherwise.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"

            >>> Dimension(TemperatureUnit.CELCIUS).isinstance(TemperatureUnit)
            True

            >>> Dimension(TemperatureUnit.CELCIUS).isinstance(TemperatureUnit**2)
            False
        """
        if isinstance(generic, MeasurementUnitType):
            generic = GenericDimension(generic)
        if not isinstance(generic, GenericDimension):
            return False

        if isinstance(self.unit, generic.unit_type) and self.power == generic.power:
            return True

        return False

    def isinstance_equivalent(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance-equivalent of the generic,
        False otherwise.

        A unit descriptor is an instance-equivalent of a generic if the generic of the
        unit descriptor is equivalent to the generic.

        Equivalence between generics is checked with the `is_equivalent` method.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            >>> class VolumeUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls): return LengthUnit**3

            >>> (LengthUnit.METER**3).isinstance_equivalent(VolumeUnit)
            True
        """
        return self.to_generic().is_equivalent(generic)

    def to_generic(self) -> GenericDimension:
        """
        Create a generic descriptor from this Dimension.

        Examples:
            >>> class AmountUnit(MeasurementUnit):
            ...     MOL = "mol"

            >>> (AmountUnit.MOL**3.56).to_generic()
            <GenericDimension: AmountUnit^3.56>
        """
        return GenericDimension(type(self.unit), self.power)

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            >>> (LengthUnit.METER**2).inverse()
            <CompositeDimension:  / (m^2)>
        """
        return CompositeDimension([], [replace(self)])

    def _isinstance_aliased(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the generic is the aliased unit descriptor of this Dimension,
        False otherwise.

        Only applicable if this Dimension's unit is of type AliasMeasurementUnit.
        """
        return (
            isinstance(self.unit, AliasMeasurementUnit)
            and (self.unit.aliased_generic_descriptor() ** self.power) == generic
        )

    def _isinstance_alias(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if this Dimension's unit is an instance of the aliased unit
        descriptor of the generic, False otherwise.

        Only applicable if generic is an AliasMeasurementUnit.
        """
        if isinstance(generic, MeasurementUnitType):
            generic = GenericDimension(generic)

        if not isinstance(generic, GenericDimension):
            return False

        if not issubclass(generic.unit_type, AliasMeasurementUnit):
            return False

        if (
            generic.unit_type.aliased_generic_descriptor() ** generic.power
            == self.to_generic()
        ):
            return True

        return False

    def __mul__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines multiplication between Dimension(s) and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     MINUTE = "min"
            >>> (TemperatureUnit.CELCIUS**3) * TimeUnit.MINUTE
            <CompositeDimension: (C^3) * min>
        """
        if isinstance(descriptor, CompositeDimension):
            numerator = descriptor.numerator.copy()
            denominator = descriptor.denominator.copy()
            numerator.append(self)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, Dimension):
            return CompositeDimension(numerator=[self, descriptor])
        if isinstance(descriptor, MeasurementUnit):
            return CompositeDimension(numerator=[self, Dimension(descriptor)])
        raise DescriptorBinaryOperationError(
            f"cannot multiply {self} with {descriptor}. "
        )

    def __truediv__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines division between Dimension(s) and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     MINUTE = "min"
            >>> (TemperatureUnit.CELCIUS**3) / TimeUnit.MINUTE
            <CompositeDimension: (C^3) / min>
        """
        if isinstance(descriptor, CompositeDimension):
            numerator = descriptor.denominator.copy()
            denominator = descriptor.numerator.copy()
            numerator.append(self)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, Dimension):
            return CompositeDimension(numerator=[self], denominator=[descriptor])
        if isinstance(descriptor, MeasurementUnit):
            return CompositeDimension(
                numerator=[self], denominator=[Dimension(descriptor)]
            )
        raise DescriptorBinaryOperationError(
            f"cannot divide {self} with  {descriptor}. "
        )

    def __pow__(self, power: float) -> "Dimension":
        """
        Defines exponentiation for Dimension(s).

        Examples:
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            >>> (TimeUnit.SECOND**2)**3
            <Dimension: s^6>
        """
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        if self.unit.is_non_dimensional():
            self.power = 1
        else:
            self.power *= power
        return self

    def __eq__(self, dimension) -> bool:
        """
        Defines equality for Dimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"
            >>> (TemperatureUnit.KELVIN**2) != TemperatureUnit.KELVIN
            True
        """
        if not isinstance(dimension, Dimension):
            return False
        return self.unit == dimension.unit and self.power == dimension.power

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        if self.power != 1:
            return f"<Dimension: {self.unit.value}^{self.power}>"
        return f"<Dimension: {self.unit.value}>"

    def __str__(self) -> str:
        s = self.unit.value
        if self.power != 1:
            return f"({s}^{self.power})"
        return s


@dataclass
class GenericCompositeDimension:
    """
    A `GenericCompositeDimension` represents a generic measurement unit that is composed
    from other generic measurement units.

    Objects of this class can represent either multiplication or division between two
    `GenericDimension` objects.

    Create objects by multiplying and diving GenericDimension or MeasurementUnitMeta
    class objects:

    Examples:
        >>> class LengthUnit(MeasurementUnit): ...
        >>> class AmountUnit(MeasurementUnit): ...

        >>> generic_molal_volume_dimension = (LengthUnit**3) / AmountUnit
        >>> generic_molal_volume_dimension
        <GenericCompositeDimension: (LengthUnit^3) / AmountUnit>
    """

    numerator: List[GenericDimension] = field(default_factory=list)
    denominator: List[GenericDimension] = field(default_factory=list)

    def to_si(self) -> "CompositeDimension":
        """
        Create a CompositeDimension with SI units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"
            ...     @classmethod
            ...     def si(cls): return cls.KELVIN
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            ...     @classmethod
            ...     def si(cls): return cls.SECOND
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            ...     @classmethod
            ...     def si(cls): return cls.METER
            >>> (TemperatureUnit * LengthUnit / TimeUnit).to_si()
            <CompositeDimension: K * m / s>
        """
        return CompositeDimension(
            [n.to_si() for n in self.numerator], [d.to_si() for d in self.denominator]
        )

    def simplify(self) -> None:
        """
        Simplify the composite by merging common dimensions.

        Examples:
            >>> class PressureUnit(AliasMeasurementUnit): ...

            >>> class TemperatureUnit(MeasurementUnit): ...

            >>> class LengthUnit(MeasurementUnit): ...

            >>> class TimeUnit(MeasurementUnit): ...

            >>> composite = (PressureUnit**(-2)) / (TemperatureUnit**(-1))
            >>> composite
            <GenericCompositeDimension: (PressureUnit^-2) / (TemperatureUnit^-1)>
            >>> composite.simplify()
            >>> composite
            <GenericCompositeDimension: TemperatureUnit / (PressureUnit^2)>

            >>> composite = PressureUnit * LengthUnit * PressureUnit / TimeUnit
            >>> composite
            <GenericCompositeDimension: LengthUnit * PressureUnit * PressureUnit / TimeUnit>
            >>> composite.simplify()
            >>> composite
            <GenericCompositeDimension: (PressureUnit^2) * LengthUnit / TimeUnit>
        """
        exponents: Dict[MeasurementUnitType, float] = {}
        for n in self.numerator:
            if n.unit_type in exponents:
                exponents[n.unit_type] += n.power
            else:
                exponents[n.unit_type] = n.power

        for d in self.denominator:
            if d.unit_type in exponents:
                exponents[d.unit_type] -= d.power
            else:
                exponents[d.unit_type] = 0 - d.power

        numerator = []
        denominator = []
        for unit_type, exponent in exponents.items():
            if exponent > 0:
                numerator.append(GenericDimension(unit_type) ** exponent)
            elif exponent < 0:
                denominator.append(GenericDimension(unit_type) ** abs(exponent))

        self.numerator = numerator
        self.denominator = denominator

    def simplified(self) -> "GenericCompositeDimension":
        """
        Returns a simplified version of this composite generic as a new object.

        Examples:
            >>> class PressureUnit(AliasMeasurementUnit): ...

            >>> class TemperatureUnit(MeasurementUnit): ...

            >>> class LengthUnit(MeasurementUnit): ...

            >>> class TimeUnit(MeasurementUnit): ...

            >>> composite = (PressureUnit**(-2)) / (TemperatureUnit**(-1))
            >>> composite
            <GenericCompositeDimension: (PressureUnit^-2) / (TemperatureUnit^-1)>
            >>> composite.simplified()
            <GenericCompositeDimension: TemperatureUnit / (PressureUnit^2)>

            >>> composite = PressureUnit * LengthUnit * PressureUnit /TimeUnit
            >>> composite
            <GenericCompositeDimension: LengthUnit * PressureUnit * PressureUnit / TimeUnit>
            >>> composite.simplified()
            <GenericCompositeDimension: (PressureUnit^2) * LengthUnit / TimeUnit>
        """
        copy = replace(self)
        copy.simplify()
        return copy

    def analyse(self) -> None:
        """
        Analyse this composite by replacing its alias units with their aliased units.

        Examples:
            >>> class MassUnit(MeasurementUnit): ...
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...

            >>> class PressureUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
            ...         return MassUnit / LengthUnit / (TimeUnit**2)

            >>> composite = PressureUnit / LengthUnit
            >>> composite
            <GenericCompositeDimension: PressureUnit / LengthUnit>

            >>> composite.analyse()
            >>> composite
            <GenericCompositeDimension: MassUnit / (TimeUnit^2) / LengthUnit / LengthUnit>
        """
        for n in self.numerator:
            if issubclass(n.unit_type, AliasMeasurementUnit):
                aliased = n.unit_type.aliased_generic_descriptor() ** n.power
                if isinstance(aliased, GenericDimension):
                    self.numerator.append(aliased)
                elif isinstance(aliased, GenericCompositeDimension):
                    self.numerator.extend(aliased.numerator)
                    self.denominator.extend(aliased.denominator)

                self.numerator.remove(n)

        for d in self.denominator:
            if issubclass(d.unit_type, AliasMeasurementUnit):
                aliased = d.unit_type.aliased_generic_descriptor() ** d.power
                if isinstance(aliased, GenericDimension):
                    self.denominator.append(aliased)
                elif isinstance(aliased, GenericCompositeDimension):
                    self.denominator.extend(aliased.numerator)
                    self.numerator.extend(aliased.denominator)

                self.denominator.remove(d)

    def analysed(self) -> "GenericCompositeDimension":
        """
        Returns an analysed version of this composite generic as a new object.

        Examples:
            >>> class MassUnit(MeasurementUnit): ...
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...

            >>> class PressureUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
            ...         return MassUnit / LengthUnit / (TimeUnit**2)

            >>> composite = PressureUnit / LengthUnit
            >>> composite
            <GenericCompositeDimension: PressureUnit / LengthUnit>

            >>> composite.analysed()
            <GenericCompositeDimension: MassUnit / (TimeUnit^2) / LengthUnit / LengthUnit>
        """
        copy = replace(self)
        copy.analyse()
        return copy

    def inverse_generic(self):
        """
        Create a generic composite with inverse units.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...

            >>> (LengthUnit / TimeUnit).inverse_generic()
            <GenericCompositeDimension: TimeUnit / LengthUnit>
        """
        return GenericCompositeDimension(
            self._denominator_copy(), self._numerator_copy()
        )

    def is_equivalent(self, other: GenericUnitDescriptor) -> bool:
        """
        Returns True if this generic is equivalent to the given one, False otherwise.

        A generic can be equivalent with another generic if the latter or the former
        is an alias.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...
            >>> class MassUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> class ForceUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return MassUnit * LengthUnit / (TimeUnit**2)

            >>> ForceUnit.is_equivalent(MassUnit * LengthUnit / (TimeUnit**2))
            True

            >>> class EnergyUnit(AliasMeasurementUnit):
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return ForceUnit * LengthUnit

            >>> EnergyUnit.is_equivalent(MassUnit * (LengthUnit**2) / (TimeUnit**2))
            True
        """
        if isinstance(other, MeasurementUnitType):
            if (
                self.denominator == []
                and len(self.numerator) == 1
                and self.numerator[0].is_equivalent(other)
            ):
                return True

            if issubclass(other, AliasMeasurementUnit):
                return other.aliased_generic_descriptor().is_equivalent(self)  # type: ignore[attr-defined]

        elif isinstance(other, GenericDimension):
            if (
                self.denominator == []
                and len(self.numerator) == 1
                and self.numerator[0].is_equivalent(other)
            ):
                return True

            if issubclass(other.unit_type, AliasMeasurementUnit):
                return (
                    other.unit_type.aliased_generic_descriptor() ** other.power
                ).is_equivalent(self)

        elif isinstance(other, GenericCompositeDimension):
            _generic = other.analysed().simplified()
            _self = self.analysed().simplified()

            return Counter(_self.numerator) == Counter(_generic.numerator) and (
                Counter(_self.denominator) == Counter(_generic.denominator)
            )

        return False

    def has_no_units(self) -> bool:
        """
        Returns True if the generic composite dimension does not have any units, False
        otherwise.

        Examples:
            >>> class LengthUnit(MeasurementUnit): ...

            >>> GenericCompositeDimension().has_no_units()
            True
            >>> GenericCompositeDimension([LengthUnit]).has_no_units()
            False
        """
        return len(self.denominator) == 0 and len(self.numerator) == 0

    def _numerator_copy(self) -> List[GenericDimension]:
        return [replace(n) for n in self.numerator]

    def _denominator_copy(self) -> List[GenericDimension]:
        return [replace(d) for d in self.denominator]

    def __mul__(self, generic: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between GenericCompositeDimension(s) and other generic
        descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> class LengthUnit(MeasurementUnit): ...
            >>> (TemperatureUnit / LengthUnit) * TimeUnit
            <GenericCompositeDimension: TemperatureUnit * TimeUnit / LengthUnit>
        """
        numerator = self.numerator.copy()
        denominator = self.denominator.copy()
        if isinstance(generic, GenericCompositeDimension):
            numerator.extend(generic.numerator)
            denominator.extend(generic.denominator)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )

        if isinstance(generic, GenericDimension):
            numerator.append(generic)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )

        if isinstance(generic, MeasurementUnitType):
            numerator.append(GenericDimension(generic))
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        raise DescriptorBinaryOperationError(f"cannot multiply {self} with {generic}. ")

    def __truediv__(
        self, generic: GenericUnitDescriptor
    ) -> "GenericCompositeDimension":
        """
        Defines division between GenericCompositeDimension(s) and other generic
        descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> class LengthUnit(MeasurementUnit): ...
            >>> (TemperatureUnit * LengthUnit) / TimeUnit
            <GenericCompositeDimension: LengthUnit * TemperatureUnit / TimeUnit>
        """
        numerator = self.numerator.copy()
        denominator = self.denominator.copy()
        if isinstance(generic, GenericCompositeDimension):
            numerator.extend(generic.denominator)
            denominator.extend(generic.numerator)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(generic, GenericDimension):
            denominator.append(generic)
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        if isinstance(generic, MeasurementUnitType):
            denominator.append(GenericDimension(generic))
            return GenericCompositeDimension(
                numerator=numerator, denominator=denominator
            )
        raise DescriptorBinaryOperationError(f"cannot divide {self} with {generic}. ")

    def __pow__(self, power: float) -> "GenericCompositeDimension":
        """
        Defines exponentiation for GenericCompositeDimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...

            >>> (TemperatureUnit / TimeUnit)**2
            <GenericCompositeDimension: (TemperatureUnit^2) / (TimeUnit^2)>
        """
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        numerator = [n**power for n in self._numerator_copy()]
        denominator = [d**power for d in self._denominator_copy()]
        return GenericCompositeDimension(numerator, denominator)

    def __eq__(self, generic) -> bool:
        """
        Defines equality for GenericCompositeDimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit): ...
            >>> class TimeUnit(MeasurementUnit): ...
            >>> (TemperatureUnit / TimeUnit) != (TimeUnit / TemperatureUnit)
            True
        """
        if not isinstance(generic, GenericCompositeDimension):
            return False
        return Counter(self.numerator) == Counter(generic.numerator) and (
            Counter(self.denominator) == Counter(generic.denominator)
        )

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        numerators = " * ".join(sorted([str(n) for n in self.numerator]))
        denominators = " / ".join(sorted([str(d) for d in self.denominator]))
        if len(denominators) > 0:
            denominators = " / " + denominators
        return numerators + denominators

    def __repr__(self) -> str:
        numerators = " * ".join(sorted([str(n) for n in self.numerator]))
        denominators = " / ".join(sorted([str(d) for d in self.denominator]))
        if len(denominators) > 0:
            denominators = " / " + denominators
        return f"<GenericCompositeDimension: {numerators + denominators}>"


@dataclass
class CompositeDimension:
    """
    A CompositeDimension represents a measurement unit that is composed from other
    measurement units.

    Objects of this class can represent either multiplication or division between two
    Dimension objects.

    Create objects by multiplying and diving Dimension or MeasurementUnit objects.

    Examples:
        >>> class LengthUnit(MeasurementUnit):
        ...     METER = "m"

        >>> class AmountUnit(MeasurementUnit):
        ...     KILO_MOL = "kmol"

        >>> molal_volume_dimension = (LengthUnit.METER**3) / AmountUnit.KILO_MOL
        >>> molal_volume_dimension
        <CompositeDimension: (m^3) / kmol>
    """

    Default = TypeVar("Default")  # default return type for `get` functions.

    numerator: List[Dimension] = field(default_factory=list)
    denominator: List[Dimension] = field(default_factory=list)

    @staticmethod
    def from_descriptor(descriptor: UnitDescriptor) -> "CompositeDimension":
        """
        Create a CompositeDimension from given descriptor.
        If descriptor is already a CompositeDimension, it returns the same object.

        This function does not serve as a constructor for CompositeDimension, rather it
        is intended to be used to convert an unknown unit descriptor to a
        CompositeDimension.

        Raises `UnitDescriptorTypeError` if given descriptor cannot be translated
        to a CompositeDimension instance.
        """
        if not isinstance(descriptor, CompositeDimension):
            raise UnitDescriptorTypeError(
                f"cannot create CompositeDimension from descriptor {descriptor}"
            )
        return descriptor

    def si(self) -> "CompositeDimension":
        """
        Returns this composite dimension in SI units.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"
            ...     RANKINE = "R"
            ...     @classmethod
            ...     def si(cls): return cls.KELVIN

            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            ...     FOOT = "ft"
            ...     @classmethod
            ...     def si(cls): return cls.METER

            >>> (TemperatureUnit.RANKINE / LengthUnit.FOOT**2).si()
            <CompositeDimension: K / (m^2)>
        """
        return CompositeDimension(
            [n.si() for n in self.numerator], [d.si() for d in self.denominator]
        )

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the CompositeDimension is an instance of the generic, False
        otherwise.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"

            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> (TemperatureUnit.CELCIUS / LengthUnit.METER).isinstance(TemperatureUnit / LengthUnit)
            True

            >>> (TemperatureUnit.CELCIUS * LengthUnit.METER).isinstance(TemperatureUnit**2)
            False
        """
        if not isinstance(generic, GenericCompositeDimension):
            return False

        return self.to_generic() == generic

    def isinstance_equivalent(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance-equivalent of the generic,
        False otherwise.

        A unit descriptor is an instance-equivalent of a generic if the generic of the
        unit descriptor is equivalent to the generic.

        Equivalence between generics is checked with the `is_equivalent` method.

        Examples:
            >>> class MassUnit(MeasurementUnit):
            ...     KILO_GRAM = "kg"
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"

            >>> class ForceUnit(AliasMeasurementUnit):
            ...     NEWTON = "N"
            ...     @classmethod
            ...     def aliased_generic_descriptor(cls):
            ...         return MassUnit * LengthUnit / (TimeUnit**2)

            >>> (MassUnit.KILO_GRAM * LengthUnit.METER / (TimeUnit.SECOND**2)).isinstance_equivalent(ForceUnit)
            True
        """
        return self.to_generic().is_equivalent(generic)

    def to_generic(self) -> GenericCompositeDimension:
        """
        Create a generic descriptor from this CompositeDimension.

        Examples:
            >>> class AmountUnit(MeasurementUnit):
            ...     MOL = "mol"

            >>> class MassUnit(MeasurementUnit):
            ...     KILO_GRAM = "kg"

            >>> (AmountUnit.MOL / MassUnit.KILO_GRAM).to_generic()
            <GenericCompositeDimension: AmountUnit / MassUnit>
        """
        return GenericCompositeDimension(
            numerator=[n.to_generic() for n in self.numerator],
            denominator=[d.to_generic() for d in self.denominator],
        )

    def get_numerator(
        self,
        generic: Union[MeasurementUnitType, GenericDimension],
        default: Optional[Default] = None,
    ) -> Union[Dimension, Optional[Default]]:
        """
        Get a dimension from the numerator. If the dimension is not found it returns
        the default.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"

            >>> composite = TemperatureUnit.KELVIN / (LengthUnit.METER**3)
            >>> composite.get_numerator(TemperatureUnit)
            <Dimension: K>
            >>> composite.get_numerator(LengthUnit, "default")
            'default'
        """
        for n in self.numerator:
            if n.isinstance(generic):
                return n
        return default

    def get_denominator(
        self,
        generic: Union[MeasurementUnitType, GenericDimension],
        default: Optional[Default] = None,
    ) -> Union[Dimension, Optional[Default]]:
        """
        Get a dimension from the denominator. If the dimension is not found it returns
        the default.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"

            >>> composite = TemperatureUnit.KELVIN / (LengthUnit.METER**3)
            >>> composite.get_denominator(LengthUnit**3)
            <Dimension: m^3>
            >>> composite.get_denominator(LengthUnit, "default")
            'default'
        """
        for d in self.denominator:
            if d.isinstance(generic):
                return d
        return default

    def simplify(self) -> None:
        """
        Simplify the composite by merging common dimensions.

        Examples:
            >>> class PressureUnit(AliasMeasurementUnit):
            ...     BAR = "bar"
            ...     PASCAL = "Pa"

            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"

            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"

            >>> composite = (PressureUnit.BAR**(-2)) / (TemperatureUnit.KELVIN**(-1))
            >>> composite
            <CompositeDimension: (bar^-2) / (K^-1)>
            >>> composite.simplify()
            >>> composite
            <CompositeDimension: K / (bar^2)>

            >>> composite = PressureUnit.PASCAL * LengthUnit.METER * PressureUnit.PASCAL /TimeUnit.SECOND
            >>> composite
            <CompositeDimension: Pa * Pa * m / s>
            >>> composite.simplify()
            >>> composite
            <CompositeDimension: (Pa^2) * m / s>
        """
        exponents: Dict[MeasurementUnit, float] = {}
        for n in self.numerator:
            if n.unit in exponents:
                exponents[n.unit] += n.power
            else:
                exponents[n.unit] = n.power

        for d in self.denominator:
            if d.unit in exponents:
                exponents[d.unit] -= d.power
            else:
                exponents[d.unit] = 0 - d.power

        numerator = []
        denominator = []
        for unit, exponent in exponents.items():
            if unit.is_non_dimensional():
                continue  # do not add non dimensional units to the simplified composite

            if exponent > 0:
                numerator.append(Dimension(unit) ** exponent)
            elif exponent < 0:
                denominator.append(Dimension(unit) ** abs(exponent))

        self.numerator = numerator
        self.denominator = denominator

    def simplified(self) -> "CompositeDimension":
        """
        Returns a simplified version of this composite dimension as a new object.

        Examples:
            >>> class PressureUnit(AliasMeasurementUnit):
            ...     BAR = "bar"
            ...     PASCAL = "Pa"

            >>> class TemperatureUnit(MeasurementUnit):
            ...     KELVIN = "K"

            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"

            >>> composite = (PressureUnit.BAR**(-2)) / (TemperatureUnit.KELVIN**(-1))
            >>> composite
            <CompositeDimension: (bar^-2) / (K^-1)>
            >>> composite.simplified()
            <CompositeDimension: K / (bar^2)>

            >>> composite = PressureUnit.PASCAL * LengthUnit.METER * PressureUnit.PASCAL /TimeUnit.SECOND
            >>> composite
            <CompositeDimension: Pa * Pa * m / s>
            >>> composite.simplified()
            <CompositeDimension: (Pa^2) * m / s>
        """
        copy = replace(self)
        copy.simplify()
        return copy

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"

            >>> (LengthUnit.METER / TimeUnit.SECOND).inverse()
            <CompositeDimension: s / m>
        """
        return CompositeDimension(self._denominator_copy(), self._numerator_copy())

    def has_no_units(self) -> bool:
        """
        Returns True if the composite dimension does not have any units, False otherwise.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     METER = "m"

            >>> CompositeDimension().has_no_units()
            True
            >>> CompositeDimension([LengthUnit.METER]).has_no_units()
            False
        """
        return len(self.denominator) == 0 and len(self.numerator) == 0

    def _numerator_copy(self) -> List[Dimension]:
        return [replace(n) for n in self.numerator]

    def _denominator_copy(self) -> List[Dimension]:
        return [replace(d) for d in self.denominator]

    def __mul__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines multiplication between CompositeDimension(s) and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            >>> (TemperatureUnit.CELCIUS / LengthUnit.CENTI_METER) * TimeUnit.SECOND
            <CompositeDimension: C * s / cm>
        """
        numerator = self.numerator.copy()
        denominator = self.denominator.copy()
        if isinstance(descriptor, CompositeDimension):
            numerator.extend(descriptor.numerator)
            denominator.extend(descriptor.denominator)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, Dimension):
            numerator.append(descriptor)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, MeasurementUnit):
            numerator.append(Dimension(descriptor))
            return CompositeDimension(numerator=numerator, denominator=denominator)
        raise DescriptorBinaryOperationError(
            f"cannot multiply {self} with {descriptor}. "
        )

    def __truediv__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines multiplication between CompositeDimension(s) and other unit descriptors.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            >>> (TemperatureUnit.CELCIUS * LengthUnit.CENTI_METER) / TimeUnit.SECOND
            <CompositeDimension: C * cm / s>
        """
        numerator = self.numerator.copy()
        denominator = self.denominator.copy()
        if isinstance(descriptor, CompositeDimension):
            numerator.extend(descriptor.denominator)
            denominator.extend(descriptor.numerator)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, Dimension):
            denominator.append(descriptor)
            return CompositeDimension(numerator=numerator, denominator=denominator)
        if isinstance(descriptor, MeasurementUnit):
            denominator.append(Dimension(descriptor))
            return CompositeDimension(numerator=numerator, denominator=denominator)
        raise DescriptorBinaryOperationError(
            f"cannot divide {self} with {descriptor}. "
        )

    def __pow__(self, power: float) -> "CompositeDimension":
        """
        Defines exponentiation for CompositeDimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     HOUR = "hr"

            >>> (TemperatureUnit.CELCIUS / TimeUnit.HOUR)**2
            <CompositeDimension: (C^2) / (hr^2)>
        """
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        numerator = [n**power for n in self._numerator_copy()]
        denominator = [d**power for d in self._denominator_copy()]
        return CompositeDimension(numerator, denominator)

    def __eq__(self, dimension) -> bool:
        """
        Defines equality for CompositeDimension(s).

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "C"
            >>> class TimeUnit(MeasurementUnit):
            ...     HOUR = "hr"
            >>> (TemperatureUnit.CELCIUS / TimeUnit.HOUR) != (TimeUnit.HOUR / TemperatureUnit.CELCIUS)
            True
        """
        if not isinstance(dimension, CompositeDimension):
            return False
        return Counter(self.numerator) == Counter(dimension.numerator) and (
            Counter(self.denominator) == Counter(dimension.denominator)
        )

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self):
        numerators = " * ".join(sorted([str(n) for n in self.numerator]))
        denominators = " / ".join(sorted([str(d) for d in self.denominator]))
        if len(denominators) > 0:
            denominators = " / " + denominators
        return numerators + denominators

    def __repr__(self) -> str:
        numerators = " * ".join(sorted([str(n) for n in self.numerator]))
        denominators = " / ".join(sorted([str(d) for d in self.denominator]))
        if len(denominators) > 0:
            denominators = " / " + denominators
        return f"<CompositeDimension: {numerators + denominators}>"
