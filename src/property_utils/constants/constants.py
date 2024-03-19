from property_utils.properties.property import Property
from property_utils.units.units import (
    EnergyUnit,
    AmountUnit,
    AbsoluteTemperatureUnit,
    LengthUnit,
    TimeUnit,
)

__all__ = [
    "GLOBAL_GAS_CONSTANT",
    "BOLTZMANN_CONSTANT",
    "VACUUM_LIGHT_SPEED",
    "AVOGADRO_NUMBER",
    "PLANCK_CONSTANT",
    "REDUCED_PLANCK_CONSTANT",
]

GLOBAL_GAS_CONSTANT = Property(
    8.31446261815324, EnergyUnit.JOULE / AmountUnit.MOL / AbsoluteTemperatureUnit.KELVIN
)
BOLTZMANN_CONSTANT = Property(
    1.380649e-13, EnergyUnit.JOULE / AbsoluteTemperatureUnit.KELVIN
)
VACUUM_LIGHT_SPEED = Property(299792458, LengthUnit.METER / TimeUnit.SECOND)
AVOGADRO_NUMBER = Property(6.02214076e23, AmountUnit.MOL.inverse())
PLANCK_CONSTANT = Property(6.62607015e-34, EnergyUnit.JOULE * TimeUnit.SECOND)
REDUCED_PLANCK_CONSTANT = Property(1.054571817e-34, EnergyUnit.JOULE * TimeUnit.SECOND)
