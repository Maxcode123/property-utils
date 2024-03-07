from property_utils.exceptions.base import PropertyUtilsTypeError


class DescriptorBinaryOperationError(PropertyUtilsTypeError):
    """
    Occurs in multiplication or division between a generic unit descriptor and a unit
    descriptor.
    """


class DescriptorExponentError(PropertyUtilsTypeError):
    """
    Invalid exponent, i.e. non-numeric.
    """


class UnitDescriptorTypeError(PropertyUtilsTypeError):
    """
    Expected different unit descriptor type.
    """
