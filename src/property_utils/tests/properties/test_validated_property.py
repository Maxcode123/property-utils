from unittest import TestSuite, TextTestRunner

from unittest_extensions import TestCase, args

from property_utils.tests.utils import add_to, def_load_tests
from property_utils.tests.data import PositiveProp, BiggerThan5Prop, Unit1, Unit2
from property_utils.exceptions.properties.property import PropertyValidationError
from property_utils.exceptions.base import PropertyUtilsException

load_tests = def_load_tests("property_utils.properties.validated_property")

validated_property_test_suite = TestSuite()


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(validated_property_test_suite)


class TestValidatedProperty(TestCase):
    def assert_validation_error(self, expected_regex=None):
        self._assert_error(PropertyValidationError, expected_regex)

    def assert_result(self, result_str):
        self.assertSequenceEqual(str(self.result()), result_str, str)

    def _assert_error(self, error: PropertyUtilsException, expected_regex):
        if expected_regex is None:
            self.assertResultRaises(error)
        else:
            self.assertResultRaisesRegex(error, expected_regex)


@add_to(validated_property_test_suite)
class TestValidatedPropertyInitWithNoUnits(TestValidatedProperty):
    def subject(self, value):
        return BiggerThan5Prop(value)

    @args({"value": "1"})
    def test_with_non_numeric(self):
        self.assert_validation_error()

    @args({"value": 2})
    def test_with_less_than_5(self):
        self.assert_validation_error()

    @args({"value": None})
    def test_with_none(self):
        self.assert_validation_error()

    @args({"value": 12.3})
    def test_with_bigger_than_5(self):
        self.assert_result("12.3 a")


@add_to(validated_property_test_suite)
class TestValidatedPropertyInit(TestValidatedProperty):
    def subject(self, unit):
        return BiggerThan5Prop(10, unit)

    @args({"unit": Unit2.B})
    def test_with_other_unit(self):
        self.assert_validation_error()

    @args({"unit": Unit1.A})
    def test_with_valid_unit(self):
        self.assert_result("10 A")

    @args({"unit": Unit1.A**2})
    def test_with_invalid_dimension(self):
        self.assert_validation_error()


@add_to(validated_property_test_suite)
class TestValidatedPropertyInitWithDefaultUnit(TestValidatedProperty):
    def subject(self, value, **kwargs):
        return PositiveProp(value, **kwargs)

    @args({"value": -1})
    def test_with_invalid_value(self):
        self.assert_validation_error()

    @args({"value": 2})
    def test_with_valid_value(self):
        self.assert_result("2 A2")

    @args({"value": 5, "unit": Unit1.a})
    def test_with_unit(self):
        self.assert_result("5 a")


@add_to(validated_property_test_suite)
class TestValidatedPropertySetValue(TestValidatedProperty):
    def subject(self, value):
        prop = BiggerThan5Prop(10, Unit1.A)
        prop.value = value
        return prop

    @args({"value": 11})
    def test_with_valid_value(self):
        self.assert_result("11 A")

    @args({"value": 2})
    def test_with_invalid_value(self):
        self.assert_validation_error()
