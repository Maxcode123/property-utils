from typing import Optional


class PropertyUtilsException(Exception):
    """
    Base exception for property-utils library. Any exception raised from the
    modules of this library should inherit from this class.
    """

    description: str

    def __init__(self, msg: Optional[str] = None, *args) -> None:
        if msg is None:
            msg = self.description
        super().__init__(msg, *args)


class InvalidDescriptorBinaryOperation(PropertyUtilsException):
    description = "invalid binary operation between descriptors. "


class InvalidDescriptorExponent(PropertyUtilsException):
    description = "invalid exponent for descriptor, i.e. not a number"


class WrongUnitDescriptorType(PropertyUtilsException):
    description = "got a wrong unit descriptor type. "


class InvalidUnitConversion(PropertyUtilsException):
    description = (
        "conversion to invalid physical property unit (e.g. from m^2 to cm^3 or from K"
        " to bar). "
    )


class UndefinedConverter(PropertyUtilsException):
    description = "a converter has not been defined for a given generic descriptor. "
