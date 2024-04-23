from dataclasses import dataclass
from typing import ClassVar, Optional
from abc import abstractmethod

from property_utils.units.descriptors import UnitDescriptor, GenericUnitDescriptor
from property_utils.properties.property import Property
from property_utils.exceptions.properties.property import PropertyValidationError


@dataclass
class ValidatedProperty(Property):
    """
    A ValidatedProperty applies custom validations on its' value.

    Inherit from this class and implement the `validate_value` method to apply a
    validation to the property's value.

    You should also define the `generic_unit_descriptor` class variable. A validation
    is applied upon initialization for the type of the unit; if its' generic type
    does not match the `generic_unit_descriptor` a PropertyValidationError` is raised.

    `default_units` class variable is the default units with which properties will be
    created; if it is not defined the default it to use SI units.

    Examples:
        >>> from property_utils.units.units import LengthUnit, AbsoluteTemperatureUnit
        >>> class Distance(ValidatedProperty):
        ...     generic_unit_descriptor = LengthUnit

        >>> class NauticalDistance(Distance):
        ...     default_units = LengthUnit.NAUTICAL_MILE

        >>> Distance(5) # defaults to SI units
        <Distance: 5 m>
        >>> NauticalDistance(45.2)
        <NauticalDistance: 45.2 NM>
    """

    generic_unit_descriptor: ClassVar[GenericUnitDescriptor]
    default_units: ClassVar[Optional[UnitDescriptor]] = None

    def __init__(self, value: float, unit: Optional[UnitDescriptor] = None) -> None:
        if unit is None:
            unit = self.default_units if self.default_units is not None else unit
            unit = self.generic_unit_descriptor.to_si() if unit is None else unit

        super().__init__(value, unit)
        if not unit.isinstance(self.generic_unit_descriptor):
            raise PropertyValidationError(
                f"cannot create {self.__class__.__name__} with {unit} units; "
                f"expected {self.generic_unit_descriptor} units. "
            )

        self.__post_init__()

    def __post_init__(self) -> None:
        self.validate_value(self.value)

    @abstractmethod
    def validate_value(self, value: float) -> None:
        """
        Validate the `value` for this property. This validation takes place after
        initialization; hence all initialized attributes are available.

        The only exception this method should raise is `PropertyValidationError`.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.value} {self.unit}>"
