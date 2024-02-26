from property_utils.units.descriptors import (
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
    def si(cls) -> "Unit3":
        return cls.c


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
