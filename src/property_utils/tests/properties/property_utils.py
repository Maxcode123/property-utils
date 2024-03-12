from abc import abstractmethod

from unittest_extensions import TestCase

from property_utils.properties.property import Property
from property_utils.exceptions.properties.property import (
    PropertyBinaryOperationError,
    PropertyUnitConversionError,
    PropertyValidationError,
)
from property_utils.exceptions.units.converter_types import UnitConversionError
from property_utils.exceptions.base import PropertyUtilsException


class TestProperty(TestCase):
    _method: str

    def setUp(self) -> None:
        self._prop = None

    def subject(self, **kwargs):
        return getattr(self.prop(), self._method)(**kwargs)

    def prop(self) -> Property:
        if self._prop is None:
            self._prop = self.build_property()
        return self._prop

    @abstractmethod
    def build_property(self) -> Property: ...

    def assert_impossible_conversion(self, expected_regex=None):
        self._assert_error(PropertyUnitConversionError, expected_regex)

    def assert_invalid_conversion(self, expected_regex=None):
        self._assert_error(UnitConversionError, expected_regex)

    def assert_invalid_operation(self, expected_regex=None):
        self._assert_error(PropertyBinaryOperationError, expected_regex)

    def assert_validation_error(self, expected_regex=None):
        self._assert_error(PropertyValidationError, expected_regex)

    def assert_result(self, result_str):
        self.assertResultIsNot(self.prop())
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)

    def _assert_error(self, error: PropertyUtilsException, expected_regex):
        if expected_regex is None:
            self.assertResultRaises(error)
        else:
            self.assertResultRaisesRegex(error, expected_regex)
