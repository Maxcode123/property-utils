"""
This module defines unit converters for the units in 'property_utils.units.units' as
well as some converters for common exponentiated units (area and volume).
"""

from enum import Enum

try:
    from typing import override  # Python >= 3.12
except ImportError:
    from typing_extensions import override  # Python < 3.12

from property_utils.units.descriptors import UnitDescriptor
from property_utils.exceptions.units.converter_types import UnitConversionError
from property_utils.units.units import (
    NonDimensionalUnit,
    RelativeTemperatureUnit,
    AbsoluteTemperatureUnit,
    LengthUnit,
    MassUnit,
    AmountUnit,
    TimeUnit,
    ElectricCurrentUnit,
    ForceUnit,
    PressureUnit,
    EnergyUnit,
    PowerUnit,
)
from property_utils.units.converter_types import (
    register_converter,
    AbsoluteUnitConverter,
    RelativeUnitConverter,
    ExponentiatedUnitConverter,
    CompositeUnitConverter,
)

__all__ = [
    "UnitPrefix",
    "RelativeTemperatureUnitConverter",
    "AbsoluteTemperatureUnitConverter",
    "LengthUnitConverter",
    "MassUnitConverter",
    "AmountUnitConverter",
    "TimeUnitConverter",
    "ElectricCurrentUnitConverter",
    "AliasForceUnitConverter",
    "AliasPressureUnitConverter",
    "AliasEnergyUnitConverter",
    "AliasPowerUnitConverter",
    "AreaUnitConverter",
    "VolumeUnitConverter",
    "ForceUnitConverter",
    "PressureUnitConverter",
    "EnergyUnitConverter",
    "PowerUnitConverter",
]


class UnitPrefix(float, Enum):
    """
    Enumeration of unit prefixes.
    Handy when converting to and fro prefixed units.

    Examples:
        >>> centimeters = 225
        >>> meters = centimeters * UnitPrefix.CENTI
        >>> meters
        2.25
    """

    PICO = 1e-12
    NANO = 1e-9
    MICRO = 1e-6
    MILLI = 1e-3
    CENTI = 1e-2
    DECI = 1e-1
    DECA = 1e1
    HECTO = 1e2
    KILO = 1e3
    MEGA = 1e6
    GIGA = 1e9
    TERA = 1e12

    def inverse(self) -> float:
        """
        Return the inverse of the unit prefix. Use when prefixing a unit.

        Examples:
            >>> meters = 50.26
            >>> centimeters = meters * UnitPrefix.CENTI.inverse()
            >>> centimeters
            5026.0
        """
        return 1 / self.value


@register_converter(RelativeTemperatureUnit)
class RelativeTemperatureUnitConverter(RelativeUnitConverter):  # pylint: disable=too-few-public-methods
    """
    Convert temperature units with this converter.

    Examples:
        >>> RelativeTemperatureUnitConverter.convert(100, RelativeTemperatureUnit.CELCIUS, RelativeTemperatureUnit.FAHRENHEIT)
        212.0
    """

    reference_unit = RelativeTemperatureUnit.CELCIUS
    conversion_map = {
        RelativeTemperatureUnit.CELCIUS: lambda t: t,
        AbsoluteTemperatureUnit.KELVIN: lambda t: t - 273.15,
        RelativeTemperatureUnit.FAHRENHEIT: lambda t: (t - 32) / 1.8,
        AbsoluteTemperatureUnit.RANKINE: lambda t: (t / 1.8) - 273.15,
    }
    reference_conversion_map = {
        RelativeTemperatureUnit.CELCIUS: lambda t: t,
        AbsoluteTemperatureUnit.KELVIN: lambda t: t + 273.15,
        RelativeTemperatureUnit.FAHRENHEIT: lambda t: (t * 1.8) + 32,
        AbsoluteTemperatureUnit.RANKINE: lambda t: (t + 273.15) * 1.8,
    }


@register_converter(AbsoluteTemperatureUnit)
class AbsoluteTemperatureUnitConverter(AbsoluteUnitConverter):
    """
    Convert absolute temperature with this converter.

    Examples:
        >>> AbsoluteTemperatureUnitConverter.convert(10, AbsoluteTemperatureUnit.KELVIN, AbsoluteTemperatureUnit.RANKINE)
        18.0
    """

    reference_unit = AbsoluteTemperatureUnit.KELVIN
    conversion_map = {
        AbsoluteTemperatureUnit.KELVIN: 1,
        AbsoluteTemperatureUnit.RANKINE: 1.8,
    }

    @override
    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        if not isinstance(value, (float, int)):
            raise UnitConversionError(f"invalid 'value': {value}; expected numeric. ")
        if from_descriptor.isinstance(
            RelativeTemperatureUnit
        ) or to_descriptor.isinstance(RelativeTemperatureUnit):
            return RelativeTemperatureUnitConverter.convert(
                value, from_descriptor, to_descriptor
            )
        return value * cls.get_factor(from_descriptor, to_descriptor)


@register_converter(NonDimensionalUnit)
class NonDimensionalUnitConverter(AbsoluteUnitConverter):
    """
    This converter is needed for compatibility, i.e. for conversions to work from
    non-dimensional units to non-dimensional dimensions.
    """

    reference_unit = NonDimensionalUnit.NON_DIMENSIONAL
    conversion_map = {NonDimensionalUnit.NON_DIMENSIONAL: 1}


@register_converter(LengthUnit)
class LengthUnitConverter(AbsoluteUnitConverter):
    """
    Convert length units with this converter.

    Examples:
        >>> LengthUnitConverter.convert(2000, LengthUnit.MILLI_METER, LengthUnit.METER)
        2.0
    """

    reference_unit = LengthUnit.METER
    conversion_map = {
        LengthUnit.MILLI_METER: UnitPrefix.MILLI.inverse(),
        LengthUnit.CENTI_METER: UnitPrefix.CENTI.inverse(),
        LengthUnit.METER: 1,
        LengthUnit.KILO_METER: UnitPrefix.KILO.inverse(),
        LengthUnit.INCH: 39.37,
        LengthUnit.FOOT: 3.281,
        LengthUnit.YARD: 1.094,
        LengthUnit.MILE: 1 / 1609,
        LengthUnit.NAUTICAL_MILE: 1 / 1852,
    }


@register_converter(MassUnit)
class MassUnitConverter(AbsoluteUnitConverter):
    """
    Convert mass units with this converter.

    Examples:
        >>> MassUnitConverter.convert(10, MassUnit.KILO_GRAM, MassUnit.GRAM)
        10000.0
    """

    reference_unit = MassUnit.KILO_GRAM
    conversion_map = {
        MassUnit.MILLI_GRAM: UnitPrefix.KILO * UnitPrefix.MILLI.inverse(),
        MassUnit.GRAM: UnitPrefix.KILO,
        MassUnit.KILO_GRAM: 1,
        MassUnit.METRIC_TONNE: 1 / 1_000.0,
        MassUnit.POUND: 2.205,
    }


@register_converter(AmountUnit)
class AmountUnitConverter(AbsoluteUnitConverter):
    """
    Convert amount units with this converter.

    Examples:
        >>> AmountUnitConverter.convert(2000, AmountUnit.MOL, AmountUnit.KILO_MOL)
        2.0
    """

    reference_unit = AmountUnit.MOL
    conversion_map = {AmountUnit.MOL: 1, AmountUnit.KILO_MOL: UnitPrefix.KILO.inverse()}


@register_converter(TimeUnit)
class TimeUnitConverter(AbsoluteUnitConverter):
    """
    Convert time units with this converter.

    Examples:
        >>> TimeUnitConverter.convert(1, TimeUnit.HOUR, TimeUnit.SECOND)
        3600.0
    """

    reference_unit = TimeUnit.SECOND
    conversion_map = {
        TimeUnit.MILLI_SECOND: UnitPrefix.MILLI.inverse(),
        TimeUnit.SECOND: 1,
        TimeUnit.MINUTE: 1 / 60.0,
        TimeUnit.HOUR: 1 / 60.0 / 60.0,
        TimeUnit.DAY: 1 / 60.0 / 60.0 / 24.0,
        TimeUnit.WEEK: 1 / 60.0 / 60.0 / 24.0 / 7,
        TimeUnit.MONTH: 1 / 60.0 / 60.0 / 24.0 / (365 / 12),
        TimeUnit.YEAR: 1 / 60.0 / 60.0 / 24.0 / 365,
    }


@register_converter(ElectricCurrentUnit)
class ElectricCurrentUnitConverter(AbsoluteUnitConverter):
    """
    Convert electric current units with this converter.

    Examples:
        >>> ElectricCurrentUnitConverter.convert(1000, ElectricCurrentUnit.MILLI_AMPERE, ElectricCurrentUnit.AMPERE)
        1.0
    """

    reference_unit = ElectricCurrentUnit.AMPERE
    conversion_map = {
        ElectricCurrentUnit.MILLI_AMPERE: UnitPrefix.MILLI.inverse(),
        ElectricCurrentUnit.AMPERE: 1,
        ElectricCurrentUnit.KILO_AMPERE: UnitPrefix.KILO.inverse(),
    }


@register_converter(ForceUnit)
class AliasForceUnitConverter(AbsoluteUnitConverter):
    """
    Convert force units with this converter.

    Examples:
        >>> AliasForceUnitConverter.convert(2, ForceUnit.NEWTON, ForceUnit.DYNE)
        200000.0
    """

    reference_unit = ForceUnit.NEWTON
    conversion_map = {ForceUnit.NEWTON: 1, ForceUnit.DYNE: 100_000}


@register_converter(PressureUnit)
class AliasPressureUnitConverter(AbsoluteUnitConverter):
    """
    Convert pressure units with this converter.

    Examples:
        >>> AliasPressureUnitConverter.convert(2, PressureUnit.BAR, PressureUnit.KILO_PASCAL)
        200.0
    """

    reference_unit = PressureUnit.BAR
    conversion_map = {
        PressureUnit.MILLI_BAR: UnitPrefix.MILLI.inverse(),
        PressureUnit.BAR: 1,
        PressureUnit.PSI: 14.5038,
        PressureUnit.PASCAL: 100_000,
        PressureUnit.KILO_PASCAL: 100,
        PressureUnit.MEGA_PASCAL: 0.1,
    }


@register_converter(EnergyUnit)
class AliasEnergyUnitConverter(AbsoluteUnitConverter):
    """
    Convert energy units with this converter.

    Examples:
        >>> AliasEnergyUnitConverter.convert(2500, EnergyUnit.JOULE, EnergyUnit.KILO_JOULE)
        2.5
    """

    reference_unit = EnergyUnit.JOULE
    conversion_map = {
        EnergyUnit.JOULE: 1,
        EnergyUnit.KILO_JOULE: UnitPrefix.KILO.inverse(),
        EnergyUnit.MEGA_JOULE: UnitPrefix.MEGA.inverse(),
        EnergyUnit.GIGA_JOULE: UnitPrefix.GIGA.inverse(),
        EnergyUnit.CALORIE: 1 / 4.184,
        EnergyUnit.KILO_CALORIE: (1 / 4.184) * UnitPrefix.KILO.inverse(),
        EnergyUnit.BTU: 1 / 1055.0,
        EnergyUnit.ELECTRONVOLT: 6.242e18,
        EnergyUnit.WATTHOUR: 1 / 3600,
        EnergyUnit.KILO_WATTHOUR: (1 / 3600) * UnitPrefix.KILO.inverse(),
    }


@register_converter(PowerUnit)
class AliasPowerUnitConverter(AbsoluteUnitConverter):
    """
    Convert power units with this converter.

    Examples:
        >>> AliasPowerUnitConverter.convert(5, PowerUnit.KILO_WATT, PowerUnit.WATT)
        5000.0
    """

    reference_unit = PowerUnit.WATT
    conversion_map = {
        PowerUnit.WATT: 1,
        PowerUnit.KILO_WATT: UnitPrefix.KILO.inverse(),
        PowerUnit.MEGA_WATT: UnitPrefix.MEGA.inverse(),
        PowerUnit.GIGA_WATT: UnitPrefix.GIGA.inverse(),
    }


@register_converter(LengthUnit**2)
class AreaUnitConverter(ExponentiatedUnitConverter):
    """
    Convert area units with this converter.

    Examples:
        >>> AreaUnitConverter.convert(1, LengthUnit.METER**2, LengthUnit.CENTI_METER**2)
        10000.0
    """


@register_converter(LengthUnit**3)
class VolumeUnitConverter(ExponentiatedUnitConverter):
    """
    Convert volume units with this converter.

    Examples:
        >>> VolumeUnitConverter.convert(1, LengthUnit.METER**3, LengthUnit.CENTI_METER**3)
        1000000.0
    """


@register_converter(ForceUnit.aliased_generic_descriptor())
class ForceUnitConverter(CompositeUnitConverter):
    """
    Convert force units (mass * length / time^2) with this converter.

    Examples:
        >>> from_unit = MassUnit.KILO_GRAM * LengthUnit.CENTI_METER / (TimeUnit.SECOND**2)
        >>> to_unit = MassUnit.GRAM * LengthUnit.METER / (TimeUnit.SECOND**2)
        >>> ForceUnitConverter.convert(100, from_unit, to_unit)
        1000.0
    """


@register_converter(PressureUnit.aliased_generic_descriptor())
class PressureUnitConverter(CompositeUnitConverter):
    """
    Convert pressure units (mass / length / time^2) with this converter.

    Examples:
        >>> from_unit = MassUnit.GRAM / LengthUnit.CENTI_METER / (TimeUnit.HOUR**2)
        >>> to_unit = MassUnit.KILO_GRAM / LengthUnit.METER / (TimeUnit.HOUR**2)
        >>> PressureUnitConverter.convert(50, from_unit, to_unit)
        5.0
    """


@register_converter(EnergyUnit.aliased_generic_descriptor())
class EnergyUnitConverter(CompositeUnitConverter):
    """
    Convert energy units (mass * length^2 / time^2) with this converter.

    Examples:
        >>> from_unit = MassUnit.KILO_GRAM * (LengthUnit.METER**2) / (TimeUnit.MINUTE**2)
        >>> to_unit = MassUnit.METRIC_TONNE * (LengthUnit.CENTI_METER**2) / (TimeUnit.MINUTE**2)
        >>> EnergyUnitConverter.convert(25, from_unit, to_unit)
        250.0
    """


@register_converter(PowerUnit.aliased_generic_descriptor())
class PowerUnitConverter(CompositeUnitConverter):
    """
    Convert power units (mass * length^2 / time^3) with this converter.

    Examples:
        >>> from_unit = MassUnit.KILO_GRAM * (LengthUnit.METER**2) / (TimeUnit.MINUTE**3)
        >>> to_unit = MassUnit.METRIC_TONNE * (LengthUnit.CENTI_METER**2) / (TimeUnit.MINUTE**3)
        >>> PowerUnitConverter.convert(15, from_unit, to_unit)
        150.0
    """
