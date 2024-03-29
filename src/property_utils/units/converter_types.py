"""
This module defines:  
Functions to fetch and register unit converters  
Unit converter protocol  
Base abstract classes for different types of unit converters  

Converters implement a 2-step process to convert 'from_unit' to 'to_unit'.  
1. Convert the 'from_unit' to a reference unit.  
2. Convert the reference unit to the 'to_unit'.
"""

from abc import ABCMeta
from typing import Protocol, Type, Callable, Dict

try:
    from typing import TypeAlias  # Python >= 3.10
except ImportError:
    from typing_extensions import TypeAlias  # Python < 3.10

from property_utils.units.descriptors import (
    MeasurementUnit,
    AliasMeasurementUnit,
    MeasurementUnitType,
    GenericDimension,
    GenericCompositeDimension,
    UnitDescriptor,
    GenericUnitDescriptor,
    Dimension,
    CompositeDimension,
)
from property_utils.exceptions.units.converter_types import (
    UndefinedConverterError,
    UnitConversionError,
    ConversionFunctionError,
    UnsupportedConverterError,
    ConverterDependenciesError,
)
from property_utils.exceptions.base import (
    PropertyUtilsTypeError,
    PropertyUtilsValueError,
)

ConverterType: TypeAlias = Type["UnitConverter"]

_converters: Dict[GenericUnitDescriptor, ConverterType] = {}


def get_converter(generic: GenericUnitDescriptor) -> ConverterType:
    """
    Get converter for given generic descriptor.

    Raises `PropertyUtilsTypeError` if argument is not a generic unit descriptor.

    Raises `UndefinedConverterError` if a converter has not been defined for the given generic.
    """
    if not isinstance(
        generic, (MeasurementUnitType, GenericDimension, GenericCompositeDimension)
    ):
        raise PropertyUtilsTypeError(
            f"cannot get converter; argument: {generic} is not a generic unit descriptor. "
        )
    if isinstance(generic, GenericDimension) and generic.power == 1:
        generic = generic.unit_type
    elif isinstance(generic, GenericDimension) and generic not in _converters:
        register_converter(generic)(
            type(f"{generic}_Converter", (ExponentiatedUnitConverter,), {})
        )
    elif isinstance(generic, GenericCompositeDimension) and generic not in _converters:
        register_converter(generic)(
            type(f"{generic}_Converter", (CompositeUnitConverter,), {})
        )
    try:
        return _converters[generic]
    except KeyError:
        raise UndefinedConverterError(
            f"a converter has not been defined for {generic}"
        ) from None


def register_converter(generic: GenericUnitDescriptor) -> Callable:
    """
    Decorate a converter class to register the generic descriptor of the units it
    operates on.
    This decorator also sets the 'generic_unit_descriptor' attribute of the decorated
    class.

    Raises `PropertyUtilsTypeError` if argument is not a generic unit descriptor.

    Raises `PropertyUtilsValueError` if generic has already a converter registered.
    """
    if not isinstance(
        generic, (MeasurementUnitType, GenericDimension, GenericCompositeDimension)
    ):
        raise PropertyUtilsTypeError(
            f"cannot get converter; argument: {generic} is not a generic unit descriptor. "
        )

    if generic in _converters:
        raise PropertyUtilsValueError(
            f"cannot register converter twice; {generic} has already got a converter. "
        )

    def wrapper(cls: ConverterType) -> ConverterType:
        _converters[generic] = cls
        cls.generic_unit_descriptor = generic
        return cls

    return wrapper


class UnitConverter(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol of classes that convert a value from one unit to another."""

    generic_unit_descriptor: GenericUnitDescriptor

    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        """
        Convert a value from a unit descriptor to its' corresponding value in a
        different unit descriptor.
        """


class AbsoluteUnitConverter(metaclass=ABCMeta):
    """
    Base converter class for measurement units that are absolute, i.e. not relative.

    e.g.
    Pressure units are absolute because the following applies:
    unit_i = unit_j * constant,
    where unit_i and unit_j can be any pressure units.

    Temperature units are not absolute because the above equation does not apply when
    converting from a relative temperature to an absolute temperature (e.g. from Celcius
    to Kelvin, or Fahrenheit to Rankine).

    Use the `register_converter` decorator when subclassing and define the
    `reference_unit` and `conversion_map` attributes. It does not matter what unit you
    shall choose to be the reference; although you have to define the conversion map
    accordingly. The conversion map is a dictionary that holds the conversion factors
    from the reference unit to other units. e.g. in the below example: 1 in = 2.54 cm

    Examples:
        >>> class LengthUnit(MeasurementUnit):
        ...     CENTI_METER = "cm"
        ...     INCH = "in"

        >>> @register_converter(LengthUnit)
        ... class LengthUnitConverter(AbsoluteUnitConverter):
        ...     reference_unit = LengthUnit.INCH
        ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}
    """

    generic_unit_descriptor: MeasurementUnitType
    reference_unit: MeasurementUnit
    conversion_map: Dict[MeasurementUnit, float]

    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        """
        Convert a value from an absolute unit to another absolute unit.
        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter or if `value`
        is not a numeric.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> LengthUnitConverter.convert(2, LengthUnit.INCH, LengthUnit.CENTI_METER)
            5.08
        """
        if not isinstance(value, (float, int)):
            raise UnitConversionError(f"invalid 'value': {value}; expected numeric. ")
        return value * cls.get_factor(from_descriptor, to_descriptor)

    @classmethod
    def get_factor(
        cls, from_descriptor: UnitDescriptor, to_descriptor: UnitDescriptor
    ) -> float:
        """
        Get the multiplication factor for the conversion from `from_descriptor` to
        `to_descriptor`.
        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> LengthUnitConverter.get_factor(LengthUnit.INCH, LengthUnit.CENTI_METER)
            2.54
        """
        if not from_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'from_descriptor; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )
        if not to_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'to_descriptor'; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )
        from_unit = MeasurementUnit.from_descriptor(from_descriptor)

        if isinstance(from_unit, AliasMeasurementUnit) and not isinstance(
            to_descriptor, AliasMeasurementUnit
        ):
            return cls._get_aliased_factor(from_unit, to_descriptor)

        to_unit = MeasurementUnit.from_descriptor(to_descriptor)
        try:
            return cls._to_reference(from_unit) * cls.conversion_map[to_unit]
        except KeyError:
            raise UnitConversionError(
                f"cannot convert to {to_unit}; unit is not registered in {cls.__name__}'s conversion map. ",
            ) from None

    @classmethod
    def _to_reference(cls, from_unit: MeasurementUnit) -> float:
        try:
            return 1 / cls.conversion_map[from_unit]
        except KeyError:
            raise UnitConversionError(
                f"cannot convert from {from_unit}; unit is not registered in {cls.__name__}'s conversion map. ",
            ) from None

    @classmethod
    def _get_aliased_factor(
        cls, from_unit: AliasMeasurementUnit, to_descriptor: UnitDescriptor
    ) -> float:
        """
        Returns the conversion factor from an alias unit to its aliased.

        The conversion happens in four steps:

        1. Convert from the alias unit to the SI unit.
        2. Convert from the SI unit to the aliased SI units (this step is not
        implemented in code, because the conversion factor is 1)
        3. Convert from the SI units to the target units.

        e.g. if you want to convert from bar to kN/m^2:
        1. bar -> Pa
        2. Pa -> N/m^2 (conversion factor 1)
        3. N/m^2 -> kN/m^2
        """
        step_1_factor = cls.get_factor(from_unit, from_unit.si())

        converter = get_converter(to_descriptor.to_generic())

        step_3_factor = converter.convert(
            1, to_descriptor.to_generic().to_si(), to_descriptor
        )

        return step_1_factor * step_3_factor


class RelativeUnitConverter(
    metaclass=ABCMeta
):  # pylint: disable=too-few-public-methods
    """
    Base converter class for measurement units that are relative.

    e.g. Temperature units are relative because conversion from one unit to another
    is not necessarily performed with multiplication with a single factor.

    Use the `register_converter` decorator when subclassing and define the
    `reference_unit`, `conversion_map` and `reference_conversion_map` attributes. It
    does not matter what unit you shall choose to be the reference; although you have to
    define the conversion map and reference conversion map accordingly. The conversion
    map is a dictionary that holds the conversion functions that convert other units to
    the reference unit. The reference conversion map is a dictionary that holds the
    conversion functions that convert the reference unit to other units.


    Examples:
        >>> class TemperatureUnit(MeasurementUnit):
        ...     CELCIUS = "°C"
        ...     FAHRENHEIT = "°F"

        >>> @register_converter(TemperatureUnit)
        ... class TemperatureUnitConverter(RelativeUnitConverter):
        ...     reference_unit = TemperatureUnit.CELCIUS
        ...     conversion_map = {
        ...             TemperatureUnit.CELCIUS: lambda t: t,
        ...             TemperatureUnit.FAHRENHEIT: lambda t: (t - 32) / 1.8,
        ...                 }
        ...     reference_conversion_map = {
        ...             TemperatureUnit.CELCIUS: lambda t: t,
        ...             TemperatureUnit.FAHRENHEIT: lambda t: (t * 1.8) + 32,
        ...                 }
    """

    generic_unit_descriptor: MeasurementUnitType
    reference_unit: MeasurementUnit
    reference_conversion_map: Dict[MeasurementUnit, Callable[[float], float]]
    conversion_map: Dict[MeasurementUnit, Callable[[float], float]]

    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        """
        Convert a value from a relative unit to another relative unit.

        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter or if `value`
        is not a numeric.

        Raises `ConversionFunctionError` if an error occurs when calling a function
        provided in the conversion_map or reference_conversion_map.

        Examples:
            >>> class TemperatureUnit(MeasurementUnit):
            ...     CELCIUS = "°C"
            ...     FAHRENHEIT = "°F"

            >>> @register_converter(TemperatureUnit)
            ... class TemperatureUnitConverter(RelativeUnitConverter):
            ...     reference_unit = TemperatureUnit.CELCIUS
            ...     conversion_map = {
            ...             TemperatureUnit.CELCIUS: lambda t: t,
            ...             TemperatureUnit.FAHRENHEIT: lambda t: (t - 32) / 1.8,
            ...                 }
            ...     reference_conversion_map = {
            ...             TemperatureUnit.CELCIUS: lambda t: t,
            ...             TemperatureUnit.FAHRENHEIT: lambda t: (t * 1.8) + 32,
            ...                 }

            >>> TemperatureUnitConverter.convert(100, TemperatureUnit.CELCIUS, TemperatureUnit.FAHRENHEIT)
            212.0
        """
        if not isinstance(value, (float, int)):
            raise UnitConversionError(f"invalid 'value': {value}; expected numeric. ")
        return cls._from_reference(
            cls._to_reference(value, from_descriptor), to_descriptor
        )

    @classmethod
    def _to_reference(cls, value: float, from_descriptor: UnitDescriptor) -> float:
        if not from_descriptor.isinstance(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'from_descriptor; expected an instance of {cls.generic_unit_descriptor}. "
            )
        from_unit = MeasurementUnit.from_descriptor(from_descriptor)
        try:
            conversion_func = cls.conversion_map[from_unit]
        except KeyError:
            raise UnitConversionError(
                f"cannot convert from {from_unit}; unit is not in {cls.__name__}'s conversion map. ",
            ) from None
        try:
            return conversion_func(value)
        except Exception as exc:
            raise ConversionFunctionError(
                f"an error occured in a conversion function of {cls.__name__}. ", exc
            ) from exc

    @classmethod
    def _from_reference(cls, value: float, to_descriptor: UnitDescriptor) -> float:
        if not to_descriptor.isinstance(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'to_descriptor'; expected an instance of {cls.generic_unit_descriptor}. "
            )
        to_unit = MeasurementUnit.from_descriptor(to_descriptor)
        try:
            conversion_func = cls.reference_conversion_map[to_unit]
        except KeyError:
            raise UnitConversionError(
                f"cannot convert to {to_unit}; unit is not registered in {cls.__name__}'s reference conversion map. ",
            ) from None
        try:
            return conversion_func(value)
        except Exception as exc:
            raise ConversionFunctionError(
                f"an error occured in a conversion function of {cls.__name__}. ", exc
            ) from exc


class ExponentiatedUnitConverter(metaclass=ABCMeta):
    """
    Base converter for exponentiated absolute measurement units.

    Use the `register_converter` decorator when subclassing. This converter requires
    the converter for the measurement unit that is exponentiated to be defined.

    Examples:
        >>> class LengthUnit(MeasurementUnit):
        ...     CENTI_METER = "cm"
        ...     INCH = "in"

        >>> @register_converter(LengthUnit)
        ... class LengthUnitConverter(AbsoluteUnitConverter):
        ...     reference_unit = LengthUnit.INCH
        ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

        >>> @register_converter(LengthUnit**2)
        ... class AreaUnitConverter(ExponentiatedUnitConverter): ...
    """

    generic_unit_descriptor: GenericDimension

    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        """
        Convert a value from an absolute exponentiated unit to another absolute
        exponentiated unit. In order to use this converter a converter must exist for
        the base unit.

        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter or if `value`
        is not a numeric.

        Raises `ConverterDependenciesError` if a converter for the base unit has not
        been defined/registered.

        Raises `UnsupportedConverterError` if the base unit is a relative unit.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> @register_converter(LengthUnit**2)
            ... class AreaUnitConverter(ExponentiatedUnitConverter): ...

            >>> AreaUnitConverter.convert(10, LengthUnit.INCH**2, LengthUnit.CENTI_METER**2)
            64.516
        """
        if not isinstance(value, (float, int)):
            raise UnitConversionError(f"invalid 'value': {value}; expected numeric. ")
        return value * cls.get_factor(from_descriptor, to_descriptor)

    @classmethod
    def get_factor(
        cls, from_descriptor: UnitDescriptor, to_descriptor: UnitDescriptor
    ) -> float:
        """
        Get the multiplication factor for the conversion from `from_descriptor` to
        `to_descriptor`.

        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter.

        Raises `ConverterDependenciesError` if a converter for the base unit has not
        been defined/registered.

        Raises `UnsupportedConverterError` if the base unit is a relative unit.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> @register_converter(LengthUnit**2)
            ... class AreaUnitConverter(ExponentiatedUnitConverter): ...

            >>> AreaUnitConverter.get_factor(LengthUnit.INCH**2, LengthUnit.CENTI_METER**2)
            6.4516
        """
        if not from_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'from_descriptor; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )
        if not to_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'to_descriptor'; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )
        from_dimension = Dimension.from_descriptor(from_descriptor)

        if not to_descriptor.isinstance(from_descriptor.to_generic()):
            if isinstance(to_descriptor, AliasMeasurementUnit):
                return cls._get_aliased_factor(from_dimension, to_descriptor)

        to_dimension = Dimension.from_descriptor(to_descriptor)

        try:
            converter = get_converter(cls.generic_unit_descriptor.unit_type)
        except UndefinedConverterError:
            raise ConverterDependenciesError(
                f"converter {cls.__name__} depends on a converter for "
                f"{cls.generic_unit_descriptor.unit_type}. Did you forget to register "
                f" a converter for {cls.generic_unit_descriptor.unit_type}? "
            ) from None
        if not issubclass(converter, AbsoluteUnitConverter):
            # NOTE: provide a link to documentation for the error.
            raise UnsupportedConverterError(
                f"converter {cls.__name__} is not supported since "
                f"{cls.generic_unit_descriptor.unit_type} is not an absolute unit;"
                " conversion between exponentiated relative units is invalid. "
            )
        factor = converter.get_factor(from_dimension.unit, to_dimension.unit)
        return factor**to_dimension.power

    @classmethod
    def _get_aliased_factor(
        cls, from_dimension: Dimension, to_descriptor: AliasMeasurementUnit
    ) -> float:
        """
        Returns the conversion factor from an alias unit to its aliased.

        The conversion happens in three steps:

        1. Convert from the alias unit to the SI unit.
        2. Convert from the SI unit to the aliased SI units (this step is not
        implemented in code, because the conversion factor is 1)
        3. Convert from the aliased SI units to the target units.

        e.g. if you want to convert from cm^3 to L:
        1. cm^3 -> m^3
        2. m^3 -> kL (conversion factor 1)
        3. kL -> L
        """
        step_1_factor = cls.get_factor(from_dimension, from_dimension.si())

        converter = get_converter(to_descriptor.to_generic())

        step_3_factor = converter.convert(
            1, to_descriptor.to_generic().to_si(), to_descriptor
        )

        return step_1_factor * step_3_factor


class CompositeUnitConverter(metaclass=ABCMeta):
    """
    Base converter for composite units.

    Use the `register_converter` decorator when subclassing. This converter requires
    the converters for the individual measurement units to be defined.

    Examples:
        >>> class LengthUnit(MeasurementUnit):
        ...     CENTI_METER = "cm"
        ...     INCH = "in"

        >>> class TimeUnit(MeasurementUnit):
        ...     SECOND = "s"
        ...     MINUTE = "min"

        >>> @register_converter(LengthUnit)
        ... class LengthUnitConverter(AbsoluteUnitConverter):
        ...     reference_unit = LengthUnit.INCH
        ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

        >>> @register_converter(TimeUnit)
        ... class TimeUnitConverter(AbsoluteUnitConverter):
        ...     reference_unit = TimeUnit.MINUTE
        ...     conversion_map = {TimeUnit.MINUTE: 1, TimeUnit.SECOND: 60}

        >>> @register_converter(LengthUnit / TimeUnit)
        ... class VelocityUnitConverter(CompositeUnitConverter): ...
    """

    generic_unit_descriptor: GenericUnitDescriptor

    @classmethod
    def convert(
        cls,
        value: float,
        from_descriptor: UnitDescriptor,
        to_descriptor: UnitDescriptor,
    ) -> float:
        """
        Convert a value from a composite unit to another composite unit.

        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter or if `value`
        is not a numeric.

        Raises `ConverterDependenciesError` if a converter for an invdividual unit has
        not been defined/registered.

        Raises `UnsupportedConverterError` if an individual unit is a relative unit.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            ...     MINUTE = "min"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> @register_converter(TimeUnit)
            ... class TimeUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = TimeUnit.MINUTE
            ...     conversion_map = {TimeUnit.MINUTE: 1, TimeUnit.SECOND: 60}

            >>> @register_converter(LengthUnit / TimeUnit)
            ... class VelocityUnitConverter(CompositeUnitConverter): ...

            >>> VelocityUnitConverter.convert(100, LengthUnit.INCH/TimeUnit.SECOND, LengthUnit.CENTI_METER/TimeUnit.SECOND)
            254.0
        """
        if not isinstance(value, (float, int)):
            raise UnitConversionError(f"invalid 'value': {value}; expected numeric. ")
        return value * cls.get_factor(from_descriptor, to_descriptor)

    @classmethod
    def get_factor(
        cls, from_descriptor: UnitDescriptor, to_descriptor: UnitDescriptor
    ) -> float:
        """
        Get the multiplication factor for the conversion from `from_descriptor` to
        `to_descriptor`.

        Raises `UnitConversionError` if `from_descriptor` or `to_descriptor` are not
        an instance of the generic that is registered with the converter.

        Raises `ConverterDependenciesError` if a converter for an invdividual unit has
        not been defined/registered.

        Raises `UnsupportedConverterError` if an individual unit is a relative unit.

        Examples:
            >>> class LengthUnit(MeasurementUnit):
            ...     CENTI_METER = "cm"
            ...     INCH = "in"

            >>> class TimeUnit(MeasurementUnit):
            ...     SECOND = "s"
            ...     MINUTE = "min"

            >>> @register_converter(LengthUnit)
            ... class LengthUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = LengthUnit.INCH
            ...     conversion_map = {LengthUnit.INCH: 1, LengthUnit.CENTI_METER: 2.54}

            >>> @register_converter(TimeUnit)
            ... class TimeUnitConverter(AbsoluteUnitConverter):
            ...     reference_unit = TimeUnit.MINUTE
            ...     conversion_map = {TimeUnit.MINUTE: 1, TimeUnit.SECOND: 60}

            >>> @register_converter(LengthUnit / TimeUnit)
            ... class VelocityUnitConverter(CompositeUnitConverter): ...

            >>> VelocityUnitConverter.get_factor(LengthUnit.INCH/TimeUnit.SECOND, LengthUnit.INCH/TimeUnit.MINUTE)
            60.0
        """
        if not from_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'from_descriptor; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )
        if not to_descriptor.isinstance_equivalent(cls.generic_unit_descriptor):
            raise UnitConversionError(
                f"invalid 'to_descriptor'; expected an instance-equivalent of {cls.generic_unit_descriptor}. "
            )

        from_dimension = CompositeDimension.from_descriptor(from_descriptor)

        if not to_descriptor.isinstance(from_descriptor.to_generic()):

            if cls._is_alias(from_dimension, to_descriptor) or (
                cls._is_aliased(from_dimension)
            ):
                return cls._get_aliased_factor(from_dimension, to_descriptor)

        to_dimension = CompositeDimension.from_descriptor(to_descriptor)
        return cls._get_numerator_factor(
            from_dimension, to_dimension
        ) / cls._get_denominator_factor(from_dimension, to_dimension)

    @classmethod
    def _get_numerator_factor(
        cls, from_dimension: CompositeDimension, to_dimension: CompositeDimension
    ) -> float:
        numerator_factor = 1.0
        for from_d in from_dimension.numerator:
            to_d = to_dimension.get_numerator(from_d.to_generic())
            if to_d is None:
                raise UnitConversionError(
                    f"cannot convert from {from_dimension} to {to_dimension}"
                )
            try:
                converter = get_converter(type(from_d.unit))
            except UndefinedConverterError:
                raise ConverterDependenciesError(
                    f"converter {cls.__name__} depends on a converter for "
                    f"{type(from_d.unit)}. Did you forget to register "
                    f" a converter for {type(from_d.unit)}? "
                ) from None
            if not issubclass(converter, AbsoluteUnitConverter):
                # NOTE: provide a link to documentation for the error.
                raise UnsupportedConverterError(
                    f"converter {cls.__name__} is not supported since "
                    f"{type(from_d.unit)} is not an absolute unit;"
                    " conversion between composite relative units is invalid. "
                )
            factor = (converter.get_factor(from_d.unit, to_d.unit)) ** from_d.power
            numerator_factor *= factor
        return numerator_factor

    @classmethod
    def _get_denominator_factor(
        cls, from_dimension: CompositeDimension, to_dimension: CompositeDimension
    ) -> float:
        denominator_factor = 1.0

        for from_d in from_dimension.denominator:
            to_d = to_dimension.get_denominator(from_d.to_generic())
            if to_d is None:
                raise UnitConversionError(
                    f"cannot convert from {from_dimension} to {to_dimension}"
                )
            try:
                converter = get_converter(type(from_d.unit))
            except UndefinedConverterError:
                raise ConverterDependenciesError(
                    f"converter {cls.__name__} depends on a converter for "
                    f"{type(from_d.unit)}. Did you forget to register "
                    f" a converter for {type(from_d.unit)}? "
                ) from None
            if not issubclass(converter, AbsoluteUnitConverter):
                # NOTE: provide a link to documentation for the error.
                raise UnsupportedConverterError(
                    f"converter {cls.__name__} is not supported since "
                    f"{type(from_d.unit)} is not an absolute unit;"
                    " conversion between composite relative units is invalid. "
                )
            factor = (converter.get_factor(from_d.unit, to_d.unit)) ** from_d.power
            denominator_factor *= factor
        return denominator_factor

    @staticmethod
    def _is_alias(
        from_dimension: CompositeDimension, descriptor: UnitDescriptor
    ) -> bool:
        """
        Returns True if the descriptor is an alias of the from_dimension.

        Assumes that from_dimension and descriptor are both an instance of the
        converter's generic unit descriptor.
        """
        if isinstance(descriptor, AliasMeasurementUnit):
            return True

        if isinstance(descriptor, Dimension):
            if isinstance(descriptor.unit, AliasMeasurementUnit):
                return True

            return False

        if isinstance(descriptor, CompositeDimension):
            for n in descriptor.numerator:
                if from_dimension.get_numerator(n.to_generic(), None) is None:
                    return True

            for d in descriptor.denominator:
                if from_dimension.get_denominator(d.to_generic(), None) is None:
                    return True

        return False

    @staticmethod
    def _is_aliased(dimension: CompositeDimension) -> bool:
        """
        Returns True if the dimension contains an alias, False otherwise.
        """
        for n in dimension.numerator:
            if isinstance(n.unit, AliasMeasurementUnit):
                return True

        for d in dimension.denominator:
            if isinstance(d.unit, AliasMeasurementUnit):
                return True

        return False

    @classmethod
    def _get_aliased_factor(
        cls, from_dimension: CompositeDimension, to_descriptor: UnitDescriptor
    ) -> float:
        """
        Returns the conversion factor from an alias unit to its aliased.

        The conversion happens in three steps:

        1. Convert from the alias unit to the SI unit.
        2. Convert from the SI unit to the aliased SI units (this step is not
        implemented in code, because the conversion factor is 1)
        3. Convert from the SI units to the target units.

        e.g. if you want to convert from cal/K/s to kW/K:
        1. cal/K/s -> J/K/s
        2. J/K/s -> W/K (conversion factor 1)
        3. W/K -> kW/K
        """
        step_1_factor = cls.get_factor(from_dimension, from_dimension.si())

        converter = get_converter(to_descriptor.to_generic())

        step_3_factor = converter.convert(
            1, to_descriptor.to_generic().to_si(), to_descriptor
        )

        return step_1_factor * step_3_factor
