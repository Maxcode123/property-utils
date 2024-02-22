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

    @classmethod
    def si(cls) -> "NonDimensionalUnit":
        return cls.NON_DIMENSIONAL


class TemperatureUnit(MeasurementUnit):
    CELCIUS = "°C"
    KELVIN = "K"
    FAHRENHEIT = "°F"
    RANKINE = "°R"

    @classmethod
    def si(cls) -> "TemperatureUnit":
        return cls.KELVIN


class AbsoluteTemperatureUnit(MeasurementUnit):
    KELVIN = "K"
    RANKINE = "°R"

    @classmethod
    def si(cls) -> "AbsoluteTemperatureUnit":
        return cls.KELVIN


class LengthUnit(MeasurementUnit):
    MILLI_METER = "mm"
    CENTI_METER = "cm"
    METER = "m"
    KILO_METER = "km"
    INCH = "in"
    FOOT = "ft"

    @classmethod
    def si(cls) -> "LengthUnit":
        return cls.METER


class MassUnit(MeasurementUnit):
    MILLI_GRAM = "mg"
    GRAM = "g"
    KILO_GRAM = "kg"
    METRIC_TONNE = "MT"
    POUND = "lb"

    @classmethod
    def si(cls) -> "MassUnit":
        return cls.KILO_GRAM


class AmountUnit(MeasurementUnit):
    MOL = "mol"
    KILO_MOL = "kmol"

    @classmethod
    def si(cls) -> "AmountUnit":
        return cls.MOL


class TimeUnit(MeasurementUnit):
    MILLI_SECOND = "ms"
    SECOND = "s"
    MINUTE = "min"
    HOUR = "hr"
    DAY = "d"

    @classmethod
    def si(cls) -> "TimeUnit":
        return cls.SECOND


class ElectricCurrentUnit(MeasurementUnit):
    MILLI_AMPERE = "mA"
    AMPERE = "A"
    KILO_AMPERE = "kA"

    @classmethod
    def si(cls) -> "ElectricCurrentUnit":
        return cls.AMPERE


class ForceUnit(AliasMeasurementUnit):
    NEWTON = "N"
    DYNE = "dyn"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return MassUnit * LengthUnit / (TimeUnit**2)

    @classmethod
    def si(cls) -> "ForceUnit":
        return cls.NEWTON


class PressureUnit(AliasMeasurementUnit):
    MILLI_BAR = "mbar"
    BAR = "bar"
    PSI = "psi"
    PASCAL = "Pa"
    KILO_PASCAL = "kPa"
    MEGA_PASCAL = "MPa"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return MassUnit / LengthUnit / (TimeUnit**2)

    @classmethod
    def si(cls) -> "PressureUnit":
        return cls.PASCAL


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

    @classmethod
    def si(cls) -> "EnergyUnit":
        return cls.JOULE


class PowerUnit(AliasMeasurementUnit):
    WATT = "W"
    KILO_WATT = "kW"
    MEGA_WATT = "MW"
    GIGA_WATT = "GW"

    @classmethod
    def aliased_generic_descriptor(cls) -> GenericCompositeDimension:
        return MassUnit * (LengthUnit**2) / (TimeUnit**3)

    @classmethod
    def si(cls) -> "PowerUnit":
        return cls.WATT
