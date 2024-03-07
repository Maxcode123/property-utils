class PropertyUtilsException(Exception):
    """
    Base exception for property-utils library. Any exception raised from the
    modules of this library inherits from this class.
    """


class PropertyUtilsValueError(PropertyUtilsException):
    """
    Wrong argument value of correct type.
    """


class PropertyUtilsTypeError(PropertyUtilsException):
    """
    Wrong argument type.
    """


class PropertyUtilsValidationError(PropertyUtilsException):
    """
    An object is created with invalid values.
    """
