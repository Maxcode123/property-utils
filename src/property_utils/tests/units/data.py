from property_utils.units.descriptors import (
    MeasurementUnit,
    AliasMeasurementUnit,
    Dimension,
    CompositeDimension,
    GenericDimension,
    GenericCompositeDimension,
)


class Unit1(MeasurementUnit):
    A = "A"
    a = "a"

    @classmethod
    def si(cls) -> "Unit1":
        return cls.a


class Unit2(MeasurementUnit):
    B = "B"
    b = "b"

    @classmethod
    def si(cls) -> "Unit2":
        return cls.b


class Unit3(AliasMeasurementUnit):
    C = "C"
    c = "c"

    @classmethod
    def si(cls) -> "Unit3":
        return cls.c


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
