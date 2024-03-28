This sections assumes the reader is acquainted with the terms in [Terminology](terminology.md).

## Unit arithmetics

### Create composite units

Units can be created by multiplying and dividing base units:

```py linenums="1"
from property_utils.units import JOULE, MOL, KELVIN, METER

thermal_capacity_units = JOULE / MOL / KELVIN
molar_volume_units = MOL / METER**3
print("thermal_capacity_units =", thermal_capacity_units)
print("molar_volume_units =", molar_volume_units)
```

Result:

```
thermal_capacity_units = J / K / mol
molar_volume_units = mol / (m^3)
```

### Compare units

Units can be compared with other units.  
The `isinstance` method checks if a unit belongs to some specific unit type.

```py linenums="1"
from property_utils.units import WATT, PowerUnit, EnergyUnit

print(WATT.isinstance(PowerUnit))
print(WATT.isinstance(EnergyUnit))
```

Result:

```
True
False
```

The `isinstance_equivalent` method checks if a unit is equivalent to some other
generic unit.

```py linenums="1"
from property_utils.units import (
    WATT,
    PowerUnit,
    EnergyUnit,
    TimeUnit,
    ForceUnit,
    LengthUnit,
    MassUnit,
)

print(WATT.isinstance_equivalent(PowerUnit))
print(WATT.isinstance_equivalent(EnergyUnit / TimeUnit))
print(WATT.isinstance_equivalent(ForceUnit * LengthUnit / TimeUnit))
print(WATT.isinstance_equivalent(MassUnit * LengthUnit**2 / TimeUnit**3))
```

Result:

```
True
True
True
True
```

### SI units
Any unit can be converted to si units with the `si` method.

```py linenums="1"
from property_utils.units import BTU, RANKINE, FOOT, CENTI_METER, KILO_CALORIE

print((BTU / FOOT**2 / RANKINE).si())
print((CENTI_METER**3).si())
print(KILO_CALORIE.si())
```

Result:

```
J / (m^2) / K
(m^3)
J
```

### Simplify composite units
Composite units may contain same units in the numerator and denominator.  
The `simplified` method removes common units from the numerator and denominator.

```py linenums="1"
from property_utils.units import METER, SECOND

velocity_units = METER / SECOND
acceleration_units = velocity_units / SECOND

print("acceleration_units =", acceleration_units)
print("acceleration_units simplified =", acceleration_units.simplified())
```

Result:

```
acceleration_units = m / s / s
acceleration_units simplified = m / (s^2)
```

The `simplified` method also merges common units.

```py linenums="1"
from property_utils.units import METER

length_units = METER
area_units = length_units * length_units

print("area_units =", area_units)
print("area_units simplified =", area_units.simplified())
```

Result:

```
area_units = m * m
area_units simplified = (m^2)
```

## Unit conversions
Any property can be converted to chosen units with `to_unit`:

```py linenums="1"
from property_utils.properties import p
from property_utils.units import WATT, METER, KELVIN, BTU, FOOT, RANKINE, HOUR

heat_transfer_coeff = p(50, WATT / METER**2 / KELVIN)
print(
    "heat_transfer_coeff =",
    heat_transfer_coeff.to_unit(BTU / HOUR / FOOT**2 / RANKINE),
)
```

Result:

```
heat_transfer_coeff = 8.805115955164156 Btu / (ft^2) / hr / °R
```

Converting to SI units is easier with `to_si`:

```py linenums="1"
from property_utils.properties import p
from property_utils.units import GRAM, CENTI_METER

area_density = p(12, GRAM / CENTI_METER**2)

print("area_density =", area_density)
print("area_density (SI) =", area_density.to_si())
```

Result:

```
area_density = 12 g / (cm^2)
area_density (SI) = 120.0 kg / (m^2)
```

## Property arithmetics

### Addition - Subtraction

Properties can be added and subtracted to and from each other:

``` py linenums="1"
from property_utils.properties import p
from property_utils.units import BAR

pressure_1 = p(15, BAR)
pressure_2 = p(2, BAR)
print("pressure_1 + pressure_2 =", pressure_1 + pressure_2)
print("pressure_1 - pressure_2 =", pressure_1 - pressure_2)
```

Result:

```
pressure_1 + pressure_2 = 17 bar
pressure_1 - pressure_2 = 13 bar
```

Properties with different units can be added to each other. The result is always calculated in the units 
of the left operand.

```py linenums="1"
from property_utils.properties import p
from property_utils.units import BAR, PSI

pressure_1 = p(5, BAR)
pressure_2 = p(30, PSI)
print("pressure_1 + pressure_2 =", pressure_1 + pressure_2)
print("pressure_2 + pressure_1 =", pressure_2 + pressure_1)
```

Result:

```
pressure_1 + pressure_2 = 7.068423447648202 bar
pressure_2 + pressure_1 = 102.519 psi
```

### Multiplication - Division

Properties can be multiplied and divided by numerics:

```py linenums="1"
from property_utils.properties import p
from property_utils.units import KELVIN

temperature = p(773.15, KELVIN)
print("2*temperature =", 2*temperature)
print("temperature/2 =", temperature/2)
```

Result:

```
2*temperature = 1546.3 K
temperature/2 = 386.575 K
```

Properties can also be multiplied and divided with each other:

```py linenums="1"
from property_utils.properties import p
from property_utils.units import KELVIN, JOULE, KILO_GRAM

thermal_capacity = p(4200, JOULE/KELVIN/KILO_GRAM)
temperature_diff = p(57, KELVIN)
enthalpy = thermal_capacity * temperature_diff
print("enthalpy =", thermal_capacity*temperature_diff)
```

Result:

```
enthalpy = 239400 J / kg
```