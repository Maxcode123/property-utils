# pylint: disable=missing-class-docstring
from property_utils.units.descriptors import (
    MeasurementUnit,
    AliasMeasurementUnit,
    GenericCompositeDimension,
)


class NonDimensionalUnit(MeasurementUnit):
    """
    This enum is used to denote physical quantities that do not have a unit of
    measurement.
    """

    NON_DIMENSIONAL = ""


class TemperatureUnit(MeasurementUnit):
    CELCIUS = "°C"
    KELVIN = "K"
    FAHRENHEIT = "°F"
    RANKINE = "°R"


class LengthUnit(MeasurementUnit):
    MILLI_METER = "mm"
    CENTI_METER = "cm"
    METER = "m"
    KILO_METER = "km"
    INCH = "in"
    FOOT = "ft"


class MassUnit(MeasurementUnit):
    MILLI_GRAM = "mg"
    GRAM = "g"
    KILO_GRAM = "kg"
    METRIC_TONNE = "MT"
    POUND = "lb"


class AmountUnit(MeasurementUnit):
    MOL = "mol"
    KILO_MOL = "kmol"


class TimeUnit(MeasurementUnit):
    MILLI_SECOND = "ms"
    SECOND = "s"
    MINUTE = "min"
    HOUR = "hr"
    DAY = "d"


class PressureUnit(AliasMeasurementUnit):
    MILLI_BAR = "mbar"
    BAR = "bar"
    PSI = "psi"
    PASCAL = "Pa"
    KILO_PASCAL = "kPa"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return MassUnit / LengthUnit / (TimeUnit**2)


class EnergyUnit(AliasMeasurementUnit):
    JOULE = "J"
    KILO_JOULE = "kJ"
    MEGA_JOULE = "MJ"
    GIGA_JOULE = "GJ"
    CALORIE = "cal"
    KILO_CALORIE = "kcal"
    BTU = "Btu"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return MassUnit * (LengthUnit**2) / (TimeUnit**2)
