# property-utils
Utilities for programming that involves physical properties

---
**Documentation:** https://maxcode123.github.io/property-utils/  
**Source code:** https://github.com/Maxcode123/property-utils  
**PyPI:** https://pypi.org/project/property-utils/  

---

## What is property-utils?
property-utils is a python library that aims at making programming with physical properties easier. It was created to be used by scientists and engineers with little programming experience.

**What is provided by property-utils?**

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
heat_exchange_area = 2 * math.pi * tube_radius * tube_length

heat_transfer_coeff = p(150, BTU / RANKINE / FOOT**2 / HOUR)

cold_in = p(273, KELVIN)
cold_out = p(300, KELVIN)
hot_in = p(520, KELVIN)
hot_out = p(472, KELVIN)
diff_in = hot_in - cold_in
diff_out = hot_out - cold_out
temperature_diff = (diff_in - diff_out) / math.log((diff_in / diff_out).value)

heat_duty = (heat_transfer_coeff * heat_exchange_area * temperature_diff).to_unit(KILO_WATT)

print(heat_duty)
```

Result:

```
306.1224518046951 kW
```