from property_utils.exceptions.base import PropertyUtilsTypeError


class InvalidDescriptorBinaryOperation(PropertyUtilsTypeError):
    """
    Occurs in multiplication or division between a generic unit descriptor and a unit
    descriptor.
    """


class InvalidDescriptorExponent(PropertyUtilsTypeError):
    """
    Invalid exponent, i.e. non-numeric.
    """


class WrongUnitDescriptorType(PropertyUtilsTypeError):
    """
    Expected different unit descriptor type.
    """
