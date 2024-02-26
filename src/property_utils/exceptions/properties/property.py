from property_utils.exceptions.base import (
    PropertyUtilsValidationError,
    PropertyUtilsTypeError,
    PropertyUtilsException,
)


class PropertyValidationError(PropertyUtilsValidationError):
    """
    A Property is constructed with invalid attributes.
    """


class PropertyUnitConversionError(PropertyUtilsException):
    """
    Cannot convert units of a Property.
    """


class PropertyBinaryOperationError(PropertyUtilsTypeError):
    """
    Invalid binary operation between Property and other object.
    """


class PropertyExponentError(PropertyUtilsTypeError):
    """
    Invalid exponent, i.e. non-numeric.
    """
