from property_utils.units.descriptors import (
    GenericUnitDescriptor,
    MeasurementUnit,
    AliasMeasurementUnit,
    Dimension,
    CompositeDimension,
    GenericDimension,
    GenericCompositeDimension,
)
from property_utils.units.converter_types import (
    register_converter,
    AbsoluteUnitConverter,
    RelativeUnitConverter,
    ExponentiatedUnitConverter,
    CompositeUnitConverter,
)
from property_utils.properties.validated_property import ValidatedProperty
from property_utils.properties.property import Property
from property_utils.exceptions.properties.property import PropertyValidationError


class Unit1(MeasurementUnit):
    A = "A"
    a = "a"
    A2 = "A2"

    @classmethod
    def si(cls) -> "Unit1":
        return cls.a


class Unit2(MeasurementUnit):
    B = "B"
    b = "b"
    B2 = "B2"
    B3 = "B3"

    @classmethod
    def si(cls) -> "Unit2":
        return cls.b


class Unit4(MeasurementUnit):
    D = "D"
    d = "d"
    D2 = "D2"

    @classmethod
    def si(cls) -> "Unit4":
        return cls.d


class Unit3(AliasMeasurementUnit):
    C = "C"
    c = "c"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericUnitDescriptor:
        return Unit1**3

    @classmethod
    def si(cls) -> "Unit3":
        return cls.c


class Unit5(AliasMeasurementUnit):
    E = "E"
    e = "e"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return Unit1 / (Unit4**2)

    @classmethod
    def si(cls) -> "Unit5":
        return cls.e


class Unit6(AliasMeasurementUnit):
    F = "F"
    f = "f"

    @classmethod
    def aliased_generic_descriptor(cls) -> Dimension:
        return Unit1**2

    @classmethod
    def si(cls) -> "Unit6":
        return cls.f


class Unit7(AliasMeasurementUnit):
    G = "G"
    g = "g"

    @classmethod
    def aliased_generic_descriptor(cls) -> CompositeDimension:
        return Unit1 / (Unit4**2) / Unit2  # Unit5 / Unit2

    @classmethod
    def si(cls) -> "Unit7":
        return cls.g


class Unit8(AliasMeasurementUnit):
    H = "H"
    h = "h"

    @classmethod
    def aliased_generic_descriptor(cls) -> CompositeDimension:
        return Unit1**2 / (Unit4**2)  # Unit6 / Unit4^2

    @classmethod
    def si(cls) -> "Unit8":
        return cls.h


class UnregisteredConverter(AbsoluteUnitConverter): ...


@register_converter(Unit1)
class Unit1Converter(AbsoluteUnitConverter):
    reference_unit = Unit1.A
    conversion_map = {Unit1.A: 1, Unit1.a: 10}


@register_converter(Unit2)
class Unit2Converter(RelativeUnitConverter):
    reference_unit = Unit2.B
    conversion_map = {
        Unit2.B: lambda u: u,
        Unit2.b: lambda u: (2 * u) + 3,
        Unit2.B3: lambda u: 15 / (u - 10),
    }
    reference_conversion_map = {
        Unit2.B: lambda u: u,
        Unit2.b: lambda u: (u - 3) / 2,
        Unit2.B3: lambda u: (15 / u) + 10,
    }


@register_converter(Unit4)
class Unit4Converter(AbsoluteUnitConverter):
    reference_unit = Unit4.D
    conversion_map = {Unit4.D: 1, Unit4.d: 5}


@register_converter(Unit5)
class Unit5Converter(AbsoluteUnitConverter):
    reference_unit = Unit5.E
    conversion_map = {Unit5.E: 1, Unit5.e: 15}


@register_converter(Unit6)
class Unit6Converter(AbsoluteUnitConverter):
    reference_unit = Unit6.F
    conversion_map = {Unit6.F: 1, Unit6.f: 2}


@register_converter(Unit7)
class Unit7Converter(AbsoluteUnitConverter):
    reference_unit = Unit7.G
    conversion_map = {Unit7.G: 1, Unit7.g: 3}


@register_converter(Unit8)
class Unit8Converter(AbsoluteUnitConverter):
    reference_unit = Unit8.H
    conversion_map = {Unit8.H: 1, Unit8.h: 4}


@register_converter(Unit1**2)
class Unit1_2Converter(ExponentiatedUnitConverter): ...


@register_converter(Unit1**3.14)
class Unit1_314Converter(ExponentiatedUnitConverter): ...


@register_converter(Unit2**4)
class Unit2_4Converter(ExponentiatedUnitConverter): ...


@register_converter(Unit3**2)
class Unit3_2Converter(ExponentiatedUnitConverter): ...


@register_converter(Unit1 * Unit2)
class Unit1Unit2Converter(CompositeUnitConverter): ...


@register_converter(Unit1 * Unit3)
class Unit1Unit3Converter(CompositeUnitConverter): ...


@register_converter(Unit1 * Unit4)
class Unit1Unit4Converter(CompositeUnitConverter): ...


@register_converter(Unit1 / Unit4)
class Unit1Unit4FractionConverter(CompositeUnitConverter): ...


@register_converter(Unit1 / (Unit4**2))
class Unit1Unit4_2Converter(CompositeUnitConverter): ...


@register_converter(Unit6 / (Unit4**2))
class Unit6Unit4_2Converter(CompositeUnitConverter): ...


@register_converter(Unit1**2 / Unit4**3)
class Unit1_2Unit4_3Converter(CompositeUnitConverter): ...


def dimension_1(power: float = 1) -> Dimension:
    """
    A^power
    """
    return Dimension(Unit1.A, power)


def dimension_2(power: float = 1) -> Dimension:
    """
    B^power
    """
    return Dimension(Unit2.B, power)


def dimension_3(power: float = 1) -> Dimension:
    """
    C^power
    """
    return Dimension(Unit3.C, power)


def dimension_4(power: float = 1) -> Dimension:
    """
    D^power
    """
    return Dimension(Unit4.D, power)


def dimension_5(power: float = 1) -> Dimension:
    """
    E^power
    """
    return Dimension(Unit5.E, power)


def dimension_6(power: float = 1) -> Dimension:
    """
    F^power
    """
    return Dimension(Unit6.F, power)


def dimension_7(power: float = 1) -> Dimension:
    """
    G^power
    """
    return Dimension(Unit7.G, power)


def generic_dimension_1(power: float = 1) -> GenericDimension:
    """
    Unit1^power
    """
    return GenericDimension(Unit1, power)


def generic_dimension_2(power: float = 1) -> GenericDimension:
    """
    Unit2^power
    """
    return GenericDimension(Unit2, power)


def generic_dimension_3(power: float = 1) -> GenericDimension:
    """
    Unit3^power
    """
    return GenericDimension(Unit3, power)


def generic_dimension_4(power: float = 1) -> GenericDimension:
    """
    Unit4^power
    """
    return GenericDimension(Unit4, power)


def generic_dimension_5(power: float = 1) -> GenericDimension:
    """
    Unit5^power
    """
    return GenericDimension(Unit5, power)


def generic_dimension_6(power: float = 1) -> GenericDimension:
    """
    Unit6^power
    """
    return GenericDimension(Unit6, power)


def generic_dimension_7(power: float = 1) -> GenericDimension:
    """
    Unit7^power
    """
    return GenericDimension(Unit7, power)


def composite_dimension() -> CompositeDimension:
    """
    (A^2) * B / (C^3)
    """
    return CompositeDimension([dimension_1(2), dimension_2()], [dimension_3(3)])


def generic_composite_dimension() -> GenericCompositeDimension:
    """
    (Unit1^2) * Unit2 / (Unit3^3)
    """
    return GenericCompositeDimension(
        [generic_dimension_1(2), generic_dimension_2()], [generic_dimension_3(3)]
    )


class BiggerThan5Prop(ValidatedProperty):
    generic_unit_descriptor = Unit1

    def validate_value(self, value: float) -> None:
        if value <= 5:
            raise PropertyValidationError


class PositiveProp(ValidatedProperty):
    generic_unit_descriptor = Unit1
    default_units = Unit1.A2

    def validate_value(self, value: float) -> None:
        if value <= 0:
            raise PropertyValidationError


class PropUnit1(Property):
    default_units = Unit1.a


class PropUnit2(Property): ...
