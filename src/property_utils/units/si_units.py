from property_utils.units.descriptors import MeasurementUnit, MeasurementUnitType
from property_utils.units.units import (
    TemperatureUnit,
    LengthUnit,
    MassUnit,
    AmountUnit,
    TimeUnit,
)


SI_UNITS: dict[MeasurementUnitType, MeasurementUnit] = {
    TemperatureUnit: TemperatureUnit.KELVIN,
    LengthUnit: LengthUnit.METER,
    MassUnit: MassUnit.KILO_GRAM,
    AmountUnit: AmountUnit.MOL,
    TimeUnit: TimeUnit.SECOND,
}
