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

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the UnitDescriptor is an instance of the generic, False
        otherwise.
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        ...     KELVIN = "K"
        ...     @classmethod
        ...     def si(cls):
        ...         return cls.KELVIN
        >>> assert TemperatureUnit.to_si() == TemperatureUnit.KELVIN
        """
        if hasattr(cls, "si"):
            return cls.si()
        raise NotImplementedError

    def inverse_generic(cls) -> "GenericCompositeDimension":
        """
        Create a generic composite with inverse units.

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> TemperatureUnit.inverse_generic()
        <GenericCompositeDimension:  / TemperatureUnit>
        """
        return GenericCompositeDimension([], [GenericDimension(cls)])

    def __mul__(cls, other: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between MeasurementUnit types and other generic
        descriptors.

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type(TemperatureUnit * TimeUnit) == GenericCompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type(TemperatureUnit / TimeUnit) == GenericCompositeDimension
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

        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type(TimeUnit**3) == GenericDimension
        """
        return GenericDimension(cls, power)

    def __str__(cls) -> str:
        return f"<MeasurementUnit: {cls.__name__}>"

    def __repr__(cls) -> str:
        return str(cls)


class MeasurementUnit(Enum, metaclass=MeasurementUnitMeta):
    """
    Base class for all measurement units of physical quantities.

    Each measurement-unit class is an enumeration of the available units for a
    quantity.

    Subclasses should only enumerate measurement units of primitive physical
    quantities, i.e. units that cannot be produced from other units.
    e.g. length is an acceptable quantity, but volume is not because its' units are
    produced from length units.

    ```
    class TemperatureUnit(MeasurementUnit):
        CELCIUS = "C"
        KELVIN = "K"
        RANKINE = "R"
        FAHRENHEIT = "F"
    ```
    """

    @classmethod
    def si(cls) -> "MeasurementUnit":
        """
        Returns the SI unit of this measurement unit.
        """
        raise NotImplementedError

    @staticmethod
    def from_descriptor(descriptor: UnitDescriptor) -> "MeasurementUnit":
        """
        Create a MeasurementUnit from given descriptor.
        If descriptor is already a MeasurementUnit, it returns the same object.

        This function does not serve as a constructor for MeasurementUnit, rather it
        is intended to be used to convert an unknown unit descriptor to a
        MeasurementUnit.

        Raises UnitDescriptorTypeError if given descriptor cannot be translated
        to a MeasurementUnit instance.

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"

        >>> celcius = MeasurementUnit.from_descriptor(TemperatureUnit.CELCIUS**2)
        >>> assert celcius == TemperatureUnit.CELCIUS
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

    def to_generic(self) -> GenericUnitDescriptor:
        """
        Create a generic descriptor from this MeasurementUnit.

        >>> class AmountUnit(MeasurementUnit):
        ...     MOL = "mol"

        >>> AmountUnit.MOL.to_generic()
        <MeasurementUnit: AmountUnit>
        """
        return self.__class__

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.

        >>> class TemperatureUnit(MeasurementUnit):
        ...     KELVIN = "K"
        >>> TemperatureUnit.KELVIN.inverse()
        <CompositeDimension:  / K>
        """
        return CompositeDimension([], [Dimension(self)])

    def __mul__(self, descriptor: UnitDescriptor) -> "CompositeDimension":
        """
        Defines multiplication between MeasurementUnit objects and other unit descriptors.

        >>> class TemperatureUnit(MeasurementUnit):
        ...     FAHRENHEIT = "F"
        >>> class TimeUnit(MeasurementUnit):
        ...     HOUR = "hr"
        >>> assert type(TemperatureUnit.FAHRENHEIT * TimeUnit.HOUR) == CompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     FAHRENHEIT = "F"
        >>> class TimeUnit(MeasurementUnit):
        ...     HOUR = "hr"
        >>> assert type(TemperatureUnit.FAHRENHEIT / TimeUnit.HOUR) == CompositeDimension
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

        >>> class LengthUnit(MeasurementUnit):
        ...     FEET = "ft"
        >>> assert type(LengthUnit.FEET**3) == Dimension
        """
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

    ```
    class PressureUnit(AliasMeasurementUnit):
        BAR = "bar"
        PASCAL = "Pa"
        KILO_PASCAL = "kPa"
        PSI = "psi"
    ```
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

        Raises UnitDescriptorTypeError if given descriptor cannot be translated
        to an AliasMeasurementUnit  instance.

        >>> class PressureUnit(AliasMeasurementUnit):
        ...     BAR = "bar"

        >>> bar = MeasurementUnit.from_descriptor(PressureUnit.BAR**(-1))
        >>> assert bar == PressureUnit.BAR
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

    >>> class MassUnit(MeasurementUnit): ...
    >>> assert type(MassUnit**2) == GenericDimension
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        ...     KELVIN = "K"
        ...     @classmethod
        ...     def si(cls): return cls.KELVIN
        >>> assert type((TemperatureUnit**2).to_si()) == Dimension
        """
        return Dimension(self.unit_type.to_si(), self.power)

    def inverse_generic(self) -> "GenericCompositeDimension":
        """
        Create a generic composite with inverse units.

        >>> class LengthUnit(MeasurementUnit): ...
        >>> (LengthUnit**2).inverse_generic()
        <GenericCompositeDimension:  / (LengthUnit^2)>
        """
        return GenericCompositeDimension([], [replace(self)])

    def __mul__(self, generic: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between GenericDimension(s) and other generic
        descriptors.

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type((TemperatureUnit**2) * TimeUnit) == GenericCompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type(TemperatureUnit / (TimeUnit**2)) == GenericCompositeDimension
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

        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert type((TimeUnit**2)**3) == GenericDimension
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

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> assert (TemperatureUnit**2) != TemperatureUnit
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

    >>> class TimeUnit(MeasurementUnit):
    ...     SECOND = "s"

    >>> assert type(TimeUnit.SECOND**2) == Dimension
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

        Raises UnitDescriptorTypeError if given descriptor cannot be translated
        to a Dimension instance.
        """
        if isinstance(descriptor, Dimension):
            return descriptor
        if isinstance(descriptor, MeasurementUnit):
            return Dimension(descriptor)
        raise UnitDescriptorTypeError(
            f"cannot create Dimension from descriptor: {descriptor}"
        )

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the Dimension is an instance of the generic, False
        otherwise.

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

    def to_generic(self) -> GenericDimension:
        """
        Create a generic descriptor from this Dimension.

        >>> class AmountUnit(MeasurementUnit):
        ...     MOL = "mol"

        >>> (AmountUnit.MOL**3.56).to_generic()
        <GenericDimension: AmountUnit^3.56>
        """
        return GenericDimension(type(self.unit), self.power)

    def inverse(self) -> "CompositeDimension":
        """
        Create a composite with inverse units.

        >>> class LengthUnit(MeasurementUnit):
        ...     METER = "m"
        >>> (LengthUnit.METER**2).inverse()
        <CompositeDimension:  / (m^2)>
        """
        return CompositeDimension([], [replace(self)])

    def __mul__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines multiplication between Dimension(s) and other unit descriptors.

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        >>> class TimeUnit(MeasurementUnit):
        ...     MINUTE = "min"
        >>> assert type((TemperatureUnit.CELCIUS**3) * TimeUnit.MINUTE) == CompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        >>> class TimeUnit(MeasurementUnit):
        ...     MINUTE = "min"
        >>> assert type((TemperatureUnit.CELCIUS**3) / TimeUnit.MINUTE) == CompositeDimension
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

        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"
        >>> assert type((TimeUnit.SECOND**2)**3) == Dimension
        """
        if not isinstance(power, (float, int)):
            raise DescriptorExponentError(
                f"invalid exponent: {{ value: {power}, type: {type(power)} }};"
                " expected float or int. "
            )
        self.power *= power
        return self

    def __eq__(self, dimension) -> bool:
        """
        Defines equality for Dimension(s).

        >>> class TemperatureUnit(MeasurementUnit):
        ...     KELVIN = "K"
        >>> assert (TemperatureUnit.KELVIN**2) != TemperatureUnit.KELVIN
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

    >>> class LengthUnit(MeasurementUnit): ...
    >>> class AmountUnit(MeasurementUnit): ...

    >>> generic_molal_volume_dimension = (LengthUnit**3) / AmountUnit
    >>> assert type(generic_molal_volume_dimension) == GenericCompositeDimension
    """

    numerator: List[GenericDimension] = field(default_factory=list)
    denominator: List[GenericDimension] = field(default_factory=list)

    def to_si(self) -> "CompositeDimension":
        """
        Create a CompositeDimension with SI units.
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
        >>> assert type((TemperatureUnit * LengthUnit / TimeUnit).to_si()) == CompositeDimension
        """
        return CompositeDimension(
            [n.to_si() for n in self.numerator], [d.to_si() for d in self.denominator]
        )

    def simplify(self) -> None:
        """
        Simplify the composite by merging common dimensions.

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

    def inverse_generic(self):
        """
        Create a generic composite with inverse units.

        >>> class LengthUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...

        >>> (LengthUnit / TimeUnit).inverse_generic()
        <GenericCompositeDimension: TimeUnit / LengthUnit>
        """
        return GenericCompositeDimension(
            self._denominator_copy(), self._numerator_copy()
        )

    def _numerator_copy(self) -> List[GenericDimension]:
        return [replace(n) for n in self.numerator]

    def _denominator_copy(self) -> List[GenericDimension]:
        return [replace(d) for d in self.denominator]

    def __mul__(self, generic: GenericUnitDescriptor) -> "GenericCompositeDimension":
        """
        Defines multiplication between GenericCompositeDimension(s) and other generic
        descriptors.

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> class LengthUnit(MeasurementUnit): ...
        >>> assert type((TemperatureUnit / LengthUnit) * TimeUnit) == GenericCompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> class LengthUnit(MeasurementUnit): ...
        >>> assert type((TemperatureUnit * LengthUnit) / TimeUnit) == GenericCompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit): ...
        >>> class TimeUnit(MeasurementUnit): ...
        >>> assert (TemperatureUnit / TimeUnit) != (TimeUnit / TemperatureUnit)
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

    Create objects by multiplying and diving Dimension or MeasurementUnit objects:
    >>> class LengthUnit(MeasurementUnit):
    ...     METER = "m"

    >>> class AmountUnit(MeasurementUnit):
    ...     KILO_MOL = "kmol"

    >>> molal_volume_dimension = (LengthUnit.METER**3) / AmountUnit.KILO_MOL
    >>> assert type(molal_volume_dimension) == CompositeDimension
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

        Raises UnitDescriptorTypeError if given descriptor cannot be translated
        to a CompositeDimension instance.
        """
        if not isinstance(descriptor, CompositeDimension):
            raise UnitDescriptorTypeError(
                f"cannot create CompositeDimension from descriptor {descriptor}"
            )
        return descriptor

    def isinstance(self, generic: GenericUnitDescriptor) -> bool:
        """
        Returns True if the CompositeDimension is an instance of the generic, False
        otherwise.

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

    def to_generic(self) -> GenericCompositeDimension:
        """
        Create a generic descriptor from this CompositeDimension.

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
            if exponent > 0:
                numerator.append(Dimension(unit) ** exponent)
            elif exponent < 0:
                denominator.append(Dimension(unit) ** abs(exponent))

        self.numerator = numerator
        self.denominator = denominator

    def simplified(self) -> "CompositeDimension":
        """
        Returns a simplified version of this composite dimension as a new object.

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

        >>> class LengthUnit(MeasurementUnit):
        ...     METER = "m"
        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"

        >>> (LengthUnit.METER / TimeUnit.SECOND).inverse()
        <CompositeDimension: s / m>
        """
        return CompositeDimension(self._denominator_copy(), self._numerator_copy())

    def _numerator_copy(self) -> List[Dimension]:
        return [replace(n) for n in self.numerator]

    def _denominator_copy(self) -> List[Dimension]:
        return [replace(d) for d in self.denominator]

    def __mul__(self, descriptor: "UnitDescriptor") -> "CompositeDimension":
        """
        Defines multiplication between CompositeDimension(s) and other unit descriptors.

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"
        >>> class LengthUnit(MeasurementUnit):
        ...     CENTI_METER = "cm"
        >>> assert type((TemperatureUnit.CELCIUS / LengthUnit.CENTI_METER) * TimeUnit.SECOND) == CompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"
        >>> class LengthUnit(MeasurementUnit):
        ...     CENTI_METER = "cm"
        >>> assert type((TemperatureUnit.CELCIUS * LengthUnit.CENTI_METER) / TimeUnit.SECOND) == CompositeDimension
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

        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "C"
        >>> class TimeUnit(MeasurementUnit):
        ...     HOUR = "hr"
        >>> assert (TemperatureUnit.CELCIUS / TimeUnit.HOUR) != (TimeUnit.HOUR / TemperatureUnit.CELCIUS)
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
