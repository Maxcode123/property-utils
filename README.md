[![image](https://img.shields.io/pypi/v/property-utils.svg)](https://pypi.python.org/pypi/property-utils)
[![image](https://img.shields.io/pypi/l/property-utils.svg)](https://opensource.org/license/mit/)
[![image](https://img.shields.io/pypi/pyversions/property-utils.svg)](https://pypi.python.org/pypi/property-utils)
[![Actions status](https://github.com/Maxcode123/property-utils/actions/workflows/test-package.yml/badge.svg?branch=main)](https://github.com/Maxcode123/property-utils/actions/workflows/test-package.yml?query=branch%3Amain)


---
**Documentation:** https://maxcode123.github.io/property-utils/  
**Source code:** https://github.com/Maxcode123/property-utils  
**PyPI:** https://pypi.org/project/property-utils/  

---

# property-utils
*Utilities for programming that involves physical properties*

## What is property-utils?
property-utils is a python library that aims at making programming with physical properties easier. It was created to be used by scientists and engineers with little programming experience.

***What is provided by property-utils?***

### Unit arithmetics
You can divide and multiply units to create new units. For example you can create velocity units by dividing length units with time units.

### Unit conversions
You can easily convert a property from one unit to another by calling a method.

### Property arithmetics
You can add, subtract, divide and multiply properties to create new properties. For example, you can create a density property by dividing a mass property with a volume property.

## Installation
```
pip install property-utils
```

## Quick usage

A simple example:

```py
import math

from property_utils.properties import p
from property_utils.units import (
    BTU,
    FOOT,
    RANKINE,
    HOUR,
    CENTI_METER,
    METER,
    KELVIN,
    KILO_WATT,
)

tube_radius = p(12, CENTI_METER)
tube_length = p(2.3, METER)
heat_exchange_area = 2 * math.pi * tube_length * tube_radius

heat_transfer_coeff = p(150, BTU / RANKINE / FOOT**2 / HOUR)

cold_in = p(273, KELVIN)
cold_out = p(300, KELVIN)
hot_in = p(520, KELVIN)
hot_out = p(472, KELVIN)
diff_in = hot_in - cold_in
diff_out = hot_out - cold_out
temperature_diff = (diff_in - diff_out) / math.log((diff_in / diff_out).value)

print("Heat transfer coefficient =", heat_transfer_coeff)
print("Heat exchange area =", heat_exchange_area)
print("Temperature difference =", temperature_diff)

heat_duty = heat_transfer_coeff * heat_exchange_area * temperature_diff

print("\nHeat duty =", heat_duty)
print("          =", heat_duty.to_si())
print("          =", heat_duty.to_unit(KILO_WATT))
```

Result:

```
Heat transfer coefficient = 150 Btu / (ft^2) / hr / °R
Heat exchange area = 1.7341591447815656 (m^2)
Logarithmic mean temperature difference = 207.24308513672648 K

Heat duty = 1044588.4611345044 Btu / hr
          = 306122.45180469507 J / s
          = 306.12245180469506 kW
```