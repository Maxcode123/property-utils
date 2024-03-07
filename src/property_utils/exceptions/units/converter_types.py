from property_utils.exceptions.base import (
    PropertyUtilsException,
    PropertyUtilsTypeError,
)


class UndefinedConverterError(PropertyUtilsException):
    """
    A converter has not been defined.
    """


class UnsupportedConverterError(PropertyUtilsException):
    """
    A converter is not supported, i.e. a converter for exponentiated relative units.
    """


class ConverterDependenciesError(PropertyUtilsException):
    """
    A converter is defined that depends on converters that have not been defined.
    """


class UnitConversionError(PropertyUtilsTypeError):
    """
    Invalid unit conversion; e.g. from TemperatureUnit to LengthUnit.

    Sub-exception of 'PropertyUtilsTypeError'.
    """


class ConversionFunctionError(PropertyUtilsException):
    """
    An error occured in a conversion function (e.g. a ZeroDivisionError).
    """
