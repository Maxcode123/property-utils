from property_utils.exceptions.base import (
    PropertyUtilsException,
    PropertyUtilsTypeError,
)


class UndefinedConverter(PropertyUtilsException):
    """
    A converter has not been defined.
    """


class UnsupportedConverter(PropertyUtilsException):
    """
    A converter is not supported, i.e. a converter for exponentiated relative units.
    """


class MissingConverterDependencies(PropertyUtilsException):
    """
    A converter is defined that depends on converters that have not been defined.
    """


class InvalidUnitConversion(PropertyUtilsTypeError):
    """
    Invalid unit conversion; e.g. from TemperatureUnit to LengthUnit.

    Sub-exception of 'PropertyUtilsTypeError'.
    """


class ConversionFunctionError(PropertyUtilsException):
    """
    An error occured in a conversion function (e.g. a ZeroDivisionError).
    """
