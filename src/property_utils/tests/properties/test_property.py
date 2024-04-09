from unittest import TestSuite, TextTestRunner

from unittest_extensions import args, TestCase

from property_utils.properties.property import Property, p
from property_utils.units.descriptors import CompositeDimension
from property_utils.units.units import NonDimensionalUnit, PressureUnit
from property_utils.exceptions.properties.property import (
    PropertyExponentError,
)
from property_utils.tests.data import (
    Unit1,
    Unit2,
    Unit3,
    Unit4,
    Unit6,
    Unit7,
    Unit8,
    generic_dimension_1,
    generic_composite_dimension,
)
from property_utils.tests.utils import add_to, def_load_tests
from property_utils.tests.properties.property_utils import TestProperty


load_tests = def_load_tests("property_utils.properties.property")

property_test_suite = TestSuite()


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(property_test_suite)


@add_to(property_test_suite)
class TestPropertyInit(TestProperty):
    def subject(self, value, unit):
        return Property(value, unit)

    @args({"value": "123", "unit": Unit1.A})
    def test_with_invalid_value(self):
        self.assert_validation_error()

    @args({"value": 2, "unit": Unit1})
    def test_with_measurement_unit_type(self):
        self.assert_validation_error()

    @args({"value": 8, "unit": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_validation_error()

    @args({"value": 0.234, "unit": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_validation_error()

    @args({"value": 8, "unit": Unit1.A})
    def test_initializes_value(self):
        self.assertEqual(self.result().value, 8)

    @args({"value": -0.1, "unit": Unit1.a})
    def test_initializes_unit(self):
        self.assertEqual(self.result().unit, Unit1.a)

    @args({"value": 0.98, "unit": Unit1.A})
    def test_does_not_initialize_converter(self):
        self.assertIsNone(self.result().unit_converter)


@add_to(property_test_suite)
class TestPropertyConstructor(TestCase):
    def subject(self, **kwargs):
        return p(**kwargs)

    @args({"value": 5})
    def test_with_no_unit(self):
        self.assertEqual(self.result().unit, NonDimensionalUnit.NON_DIMENSIONAL)

    @args({"value": 5, "unit": PressureUnit.BAR})
    def test_with_unit(self):
        self.assertEqual(self.result().unit, PressureUnit.BAR)


@add_to(property_test_suite, "eq")
class TestPropertyEq(TestProperty):

    def build_property(self):
        return Property(33.333333, Unit1.A)

    @args({"other": 5})
    def test_with_numeric(self):
        self.assertResultFalse()

    @args({"other": Property(33.33333, Unit4.D)})
    def test_with_other_unit_type(self):
        self.assertResultFalse()

    @args({"other": Property(33.33333, Unit1.A)})
    def test_without_tolerance(self):
        self.assertResultFalse()

    @args({"other": Property(33.33333, Unit1.A), "rel_tol": 0.00000001})
    def test_with_small_relative_tolerance(self):
        self.assertResultFalse()

    @args({"other": Property(33.33333, Unit1.A), "rel_tol": 0.1})
    def test_with_big_relative_tolerance(self):
        self.assertResultTrue()

    @args({"other": Property(33.33333, Unit1.A), "abs_tol": 0.000001})
    def test_with_small_absolute_tolerance(self):
        self.assertResultFalse()

    @args({"other": Property(33.33333, Unit1.A), "abs_tol": 0.1})
    def test_with_big_absolute_tolerance(self):
        self.assertResultTrue()

    @args({"other": Property(33.33333, Unit1.A), "rel_tol": 0.00000001, "abs_tol": 0.1})
    def test_with_small_relative_big_absolute(self):
        self.assertResultTrue()

    @args({"other": Property(33.33333, Unit1.A), "rel_tol": 0.1, "abs_tol": 0.00000001})
    def test_with_big_relative_small_absolute(self):
        self.assertResultTrue()

    @args({"other": Property(333.3333, Unit1.a)})
    def test_other_units_without_tolerance(self):
        self.assertResultFalse()

    @args({"other": Property(33.3333, Unit1.A2)})
    def test_with_uneregistered_units(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "eq")
class TestAliasPropertyEq(TestProperty):
    def build_property(self):
        return Property(10, Unit8.H)

    @args({"other": Property(10, Unit8.H)})
    def test_with_same_unit(self):
        self.assertResultTrue()

    @args({"other": Property(40, Unit8.h)})
    def test_with_si_unit(self):
        self.assertResultTrue()

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(10, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assertResultTrue()

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(500, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assertResultTrue()


@add_to(property_test_suite)
class TestPropertyToSi(TestProperty):
    def subject(self, unit):
        return Property(200, unit).to_si()

    @args({"unit": Unit1.a})
    def test_with_simple_si_units(self):
        self.assert_result("200 a")

    @args({"unit": Unit1.a**2})
    def test_with_dimension_si_units(self):
        self.assert_result("200 (a^2)")

    @args({"unit": (Unit1.a**2) / (Unit4.d**3)})
    def test_with_composite_si_units(self):
        self.assert_result("200 (a^2) / (d^3)")

    @args({"unit": Unit1.A})
    def test_with_simple_non_si_units(self):
        self.assert_result("2000.0 a")

    @args({"unit": Unit1.A**2})
    def test_with_dimension_non_si_units(self):
        self.assert_result("20000.0 (a^2)")

    @args({"unit": Unit1.A / Unit4.D})
    def test_with_composite_non_si_units(self):
        self.assert_result("400.0 a / d")

    @args({"unit": Unit1.A**4})
    def test_with_dimension_unregistered_unit_converter(self):
        self.assert_result("2000000.0 (a^4)")

    @args({"unit": Unit3.C})
    def test_with_simple_unit_unregistered_unit_converter(self):
        self.assert_impossible_conversion()


@add_to(property_test_suite, "to_unit")
class TestSimplePropertyToUnit(TestProperty):

    def build_property(self):
        return Property(105, Unit1.A)

    @args({"unit": Unit2.B})
    def test_with_different_unit_type(self):
        self.assert_impossible_conversion()

    @args({"unit": Unit1.A})
    def test_with_same_unit(self):
        self.assert_result("105 A")

    @args({"unit": Unit1.a})
    def test_with_other_unit(self):
        self.assert_result("1050.0 a")

    @args({"unit": Unit1.A2})
    def test_with_unregistered_unit(self):
        self.assert_invalid_conversion()


@add_to(property_test_suite, "to_unit")
class TestPropertyToUnit(TestProperty):

    def build_property(self):
        return Property(52, Unit1.A**2)

    @args({"unit": Unit2.B**2})
    def test_with_different_dimension(self):
        self.assert_impossible_conversion()

    @args({"unit": Unit1.A**2})
    def test_with_same_dimension(self):
        self.assert_result("52 (A^2)")

    @args({"unit": Unit1.a**2})
    def test_with_other_unit(self):
        self.assert_result("5200.0 (a^2)")

    @args({"unit": Unit1.A2**2})
    def test_with_unregistered_unit(self):
        self.assert_invalid_conversion()


@add_to(property_test_suite, "to_unit")
class TestCompositePropertyToUnit(TestProperty):

    def build_property(self):
        return Property(20, (Unit1.A**2) / (Unit4.D**3))

    @args({"unit": Unit1.A / Unit4.D})
    def test_with_different_composite_dimension(self):
        self.assert_impossible_conversion()

    @args({"unit": (Unit1.A**2) / (Unit4.D**3)})
    def test_with_same_composite_dimension(self):
        self.assert_result("20 (A^2) / (D^3)")

    @args({"unit": (Unit1.a**2) / (Unit4.d**3)})
    def test_with_other_unit(self):
        self.assert_result("16.0 (a^2) / (d^3)")

    @args({"unit": (Unit1.A2**2) / (Unit4.D**3)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_conversion()


@add_to(property_test_suite)
class TestPropertyNegation(TestProperty):
    def subject(self, value):
        return -Property(value, Unit1.A).value

    @args({"value": 5})
    def test_with_positive(self):
        self.assertResult(-5)

    @args({"value": -7})
    def test_with_negative(self):
        self.assertResult(7)


@add_to(property_test_suite, "__mul__")
class TestPropertyMultiplication(TestProperty):

    def build_property(self):
        return Property(5.2, Unit1.A)

    @args({"other": "287"})
    def test_with_string(self):
        self.assert_invalid_operation()

    @args({"other": None})
    def test_with_none(self):
        self.assert_invalid_operation()

    @args({"other": 1})
    def test_with_1(self):
        self.assert_result("5.2 A")

    @args({"other": 5})
    def test_with_5(self):
        self.assert_result("26.0 A")

    @args({"other": 0})
    def test_with_0(self):
        self.assert_result("0.0 A")

    @args({"other": -2})
    def test_with_minus_2(self):
        self.assert_result("-10.4 A")

    @args({"other": Property(2, Unit1.A**2.3)})
    def test_with_exponentiated_property(self):
        self.assert_result("10.4 (A^3.3)")

    @args({"other": Property(2, Unit1.A ** (-1))})
    def test_with_inverse_property(self):
        self.assert_result("10.4 ")

    @args({"other": Property(4, Unit2.B)})
    def test_with_other_propperty(self):
        self.assert_result("20.8 A * B")

    @args({"other": Property(10, Unit1.A * Unit2.B / Unit3.C)})
    def test_with_complex_property(self):
        self.assert_result("52.0 (A^2) * B / C")

    @args({"other": Property(0, (Unit1.A**2) / (Unit2.B**3))})
    def test_with_zero_value_property(self):
        self.assert_result("0.0 (A^3) / (B^3)")


@add_to(property_test_suite, "__mul__")
class TestCompositeDimensionPropertyUnitPreconversionMultiplication(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A * Unit4.d**2 / Unit6.F / Unit8.H**3)

    @args({"other": Property(1, Unit6.f / Unit1.a)})
    def test_with_composite_unit_simplify_numerator_and_denominator(self):
        self.assert_result("5.0 (d^2) / (H^3)")

    @args({"other": Property(1, Unit1.a / Unit6.f)})
    def test_with_composite_unit_add_to_numerator_and_denominator(self):
        self.assert_result("0.2 (A^2) * (d^2) / (F^2) / (H^3)")

    @args({"other": Property(64, Unit8.h**3)})
    def test_with_dimension_same_denominator(self):
        self.assert_result("1.0 (d^2) * A / F")

    @args({"other": Property(16, Unit8.h**2)})
    def test_with_dimension_denominator(self):
        self.assert_result("1.0 (d^2) * A / F / H")

    @args({"other": Property(100, Unit1.a**2)})
    def test_with_dimension_numerator(self):
        self.assert_result_almost("1.0 (A^3) * (d^2) / (H^3) / F")

    @args({"other": Property(1, Unit4.D)})
    def test_with_unit_same_numerator(self):
        self.assert_result("5.0 (d^3) * A / (H^3) / F")

    @args({"other": Property(2, Unit6.f)})
    def test_with_unit_same_denominator(self):
        self.assert_result("1.0 (d^2) * A / (H^3)")


@add_to(property_test_suite, "__mul__")
class TestDimensionPropertyUnitPreconversionMultiplication(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A**2)

    @args({"other": Property(1, Unit4.d / Unit1.a)})
    def test_with_composite_dimension_denominator(self):
        self.assert_result("10.0 A * d")

    @args({"other": Property(10, Unit1.a / Unit4.d)})
    def test_with_composite_dimension_numerator(self):
        self.assert_result("1.0 (A^3) / d")

    @args({"other": Property(1, Unit4.d / Unit1.a**2)})
    def test_with_composite_dimension_same_denominator(self):
        self.assert_result_almost("100.0 d")

    @args({"other": Property(1000, Unit1.a**3)})
    def test_with_same_unit_dimension(self):
        self.assert_result_almost("1.0 (A^5)")

    @args({"other": Property(10, Unit1.a)})
    def test_with_same_unit(self):
        self.assert_result("1.0 (A^3)")


@add_to(property_test_suite, "__mul__")
class TestUnitPropertyUnitPreconversionMultiplication(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A)

    @args({"other": Property(1, Unit4.d / Unit1.a)})
    def test_with_composite_dimension_same_denominator(self):
        self.assert_result("10.0 d")

    @args({"other": Property(10, Unit1.a / Unit4.d)})
    def test_with_composite_dimension_same_numerator(self):
        self.assert_result("1.0 (A^2) / d")

    @args({"other": Property(1, Unit4.d / Unit1.a**2)})
    def test_with_composite_dimension(self):
        self.assert_result_almost("100.0 d / A")

    @args({"other": Property(100, Unit1.a**2)})
    def test_with_dimension_same_unit(self):
        self.assert_result_almost("1.0 (A^3)")

    @args({"other": Property(10, Unit1.a)})
    def test_with_same_unit(self):
        self.assert_result("1.0 (A^2)")


@add_to(property_test_suite, "__truediv__")
class TestPropertyDivision(TestProperty):

    def build_property(self):
        return Property(6, Unit1.A)

    @args({"other": "2.34"})
    def test_with_string(self):
        self.assert_invalid_operation()

    @args({"other": None})
    def test_with_none(self):
        self.assert_invalid_operation()

    @args({"other": 1})
    def test_with_1(self):
        self.assert_result("6.0 A")

    @args({"other": 3})
    def test_with_3(self):
        self.assert_result("2.0 A")

    @args({"other": 0})
    def test_with_0(self):
        self.assert_invalid_operation()

    @args({"other": -2})
    def test_with_minus_2(self):
        self.assert_result("-3.0 A")

    @args({"other": Property(2, Unit1.A**3)})
    def test_with_exponentiated_property(self):
        self.assert_result("3.0  / (A^2)")

    @args({"other": Property(2, Unit1.A)})
    def test_with_same_property(self):
        self.assert_result("3.0 ")

    @args({"other": Property(2, Unit2.B)})
    def test_with_other_propperty(self):
        self.assert_result("3.0 A / B")

    @args({"other": Property(10, Unit1.A * Unit2.B / Unit3.C)})
    def test_with_complex_property(self):
        self.assert_result("0.6 C / B")

    @args({"other": Property(0, (Unit1.A**2) / (Unit2.B**3))})
    def test_with_zero_value_property(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "__truediv__")
class TestCompositeDimensionPropertyUnitPreconversionDivision(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A * Unit4.d**2 / Unit6.F / Unit8.H**3)

    @args({"other": Property(1, Unit6.f / Unit1.a)})
    def test_with_composite_unit_add_to_numerator_and_denominator(self):
        self.assert_result("0.2 (A^2) * (d^2) / (F^2) / (H^3)")

    @args({"other": Property(1, Unit1.a / Unit6.f)})
    def test_with_composite_unit_simplify_numerator_and_denominator(self):
        self.assert_result("5.0 (d^2) / (H^3)")

    @args({"other": Property(1, Unit8.h**3)})
    def test_with_dimension_same_denominator(self):
        self.assert_result("64.0 (d^2) * A / (H^6) / F")

    @args({"other": Property(1, Unit8.h**2)})
    def test_with_dimension_denominator(self):
        self.assert_result("16.0 (d^2) * A / (H^5) / F")

    @args({"other": Property(1, Unit1.a**2)})
    def test_with_dimension_numerator(self):
        self.assert_result_almost("100.0 (d^2) / (H^3) / A / F")

    @args({"other": Property(1, Unit4.D)})
    def test_with_unit_same_numerator(self):
        self.assert_result("0.2 A * d / (H^3) / F")

    @args({"other": Property(2, Unit6.f)})
    def test_with_unit_same_denominator(self):
        self.assert_result("1.0 (d^2) * A / (F^2) / (H^3)")


@add_to(property_test_suite, "__truediv__")
class TestDimensionPropertyUnitPreconversionDivision(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A**2)

    @args({"other": Property(1, Unit4.d / Unit1.a)})
    def test_with_composite_dimension_denominator(self):
        self.assert_result("0.1 (A^3) / d")

    @args({"other": Property(1, Unit1.a / Unit4.d)})
    def test_with_composite_dimension_numerator(self):
        self.assert_result("10.0 A * d")

    @args({"other": Property(1, Unit4.d / Unit1.a**2)})
    def test_with_composite_dimension_same_denominator(self):
        self.assert_result_almost("0.01 (A^4) / d")

    @args({"other": Property(1000, Unit1.a**3)})
    def test_with_same_unit_dimension(self):
        self.assert_result_almost("1.0  / A")

    @args({"other": Property(10, Unit1.a)})
    def test_with_same_unit(self):
        self.assert_result("1.0 A")


@add_to(property_test_suite, "__truediv__")
class TestUnitPropertyUnitPreconversionDivision(TestProperty):

    def build_property(self) -> Property:
        return Property(1, Unit1.A)

    @args({"other": Property(1, Unit4.d / Unit1.a)})
    def test_with_composite_dimension_same_denominator(self):
        self.assert_result("0.1 (A^2) / d")

    @args({"other": Property(10, Unit1.a / Unit4.d)})
    def test_with_composite_dimension_same_numerator(self):
        self.assert_result("1.0 d")

    @args({"other": Property(1, Unit4.d / Unit1.a**2)})
    def test_with_composite_dimension(self):
        self.assert_result_almost("0.01 (A^3) / d")

    @args({"other": Property(100, Unit1.a**2)})
    def test_with_dimension_same_unit(self):
        self.assert_result_almost("1.0  / A")

    @args({"other": Property(10, Unit1.a)})
    def test_with_same_unit(self):
        self.assert_result("1.0 ")


@add_to(property_test_suite, "__rtruediv__")
class TestPropertyRightDivision(TestProperty):

    def build_property(self):
        return Property(10, Unit1.A)

    @args({"other": "2.34"})
    def test_with_string(self):
        self.assert_invalid_operation()

    @args({"other": None})
    def test_with_none(self):
        self.assert_invalid_operation()

    @args({"other": 1})
    def test_with_1(self):
        self.assert_result("0.1  / A")

    @args({"other": 3})
    def test_with_3(self):
        self.assert_result("0.3  / A")

    @args({"other": 0})
    def test_with_0(self):
        self.assert_result("0.0  / A")

    @args({"other": -2})
    def test_with_minus_2(self):
        self.assert_result("-0.2  / A")

    @args({"other": Property(2, Unit1.A**3)})
    def test_with_exponentiated_property(self):
        self.assert_result("0.2 (A^2)")

    @args({"other": Property(2, Unit1.A)})
    def test_with_same_property(self):
        self.assert_result("0.2 ")

    @args({"other": Property(2, Unit2.B)})
    def test_with_other_propperty(self):
        self.assert_result("0.2 B / A")

    @args({"other": Property(10, Unit1.A * Unit2.B / Unit3.C)})
    def test_with_complex_property(self):
        self.assert_result("1.0 B / C")

    @args({"other": Property(0, (Unit1.A**2) / (Unit2.B**3))})
    def test_with_zero_value_property(self):
        self.assert_result("0.0 A / (B^3)")


@add_to(property_test_suite, "__add__")
class TestSimpleProppertyAddition(TestProperty):

    def build_property(self):
        return Property(2.3, Unit1.A)

    @args({"other": 5})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(2, Unit2.B)})
    def test_with_other_unit_type_property(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(30, Unit1.a)})
    def test_with_other_units_property(self):
        self.assert_result("5.3 A")

    @args({"other": Property(5, Unit1.A)})
    def test_with_same_units_property(self):
        self.assert_result("7.3 A")

    @args({"other": -Property(10, Unit1.A)})
    def test_with_negative(self):
        self.assert_result("-7.7 A")

    @args({"other": Property(0, Unit1.a)})
    def test_with_zero_value(self):
        self.assert_result("2.3 A")


@add_to(property_test_suite, "__add__")
class TestPropertyAddition(TestProperty):

    def build_property(self):
        return Property(5, Unit1.A * Unit2.B / Unit4.D)

    @args({"other": Property(0, Unit1.A * Unit2.B)})
    def test_with_numerator_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(2, Unit4.D)})
    def test_with_denominator_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, (Unit1.A * Unit2.B / Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "__add__")
class TestPropertyAdditionWithUnregisteredUnitConverter(TestProperty):

    def build_property(self):
        return Property(10, Unit3.C)

    @args({"other": Property(3, Unit3.C)})
    def test_with_same_units(self):
        self.assert_result("13 C")

    @args({"other": Property(3, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "__add__")
class TestAliasPropertyAddition(TestProperty):
    def build_property(self) -> Property:
        return Property(15, Unit8.H)

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assert_result("25.0 H")

    @args({"other": Property(15, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assert_result("30.0 H")

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assert_result("25.0 H")

    @args({"other": Property(500, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assert_result("25.0 H")


@add_to(property_test_suite, "__sub__")
class TestSimplePropertySubtraction(TestProperty):

    def build_property(self):
        return Property(15, Unit1.A)

    @args({"other": 4})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(10, Unit2.B)})
    def test_with_other_unit_type_property(self):
        self.assert_invalid_operation()

    @args({"other": Property(10, Unit1.A2)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(20, Unit1.A)})
    def test_with_same_unit(self):
        self.assert_result("-5 A")

    @args({"other": Property(20, Unit1.a)})
    def test_with_different_unit(self):
        self.assert_result("13.0 A")

    @args({"other": -Property(10, Unit1.A)})
    def test_with_negative(self):
        self.assert_result("25 A")

    @args({"other": Property(0, Unit1.a)})
    def test_with_zero_value(self):
        self.assert_result("15.0 A")


@add_to(property_test_suite, "__sub__")
class TestPropertySubtraction(TestProperty):

    def build_property(self):
        return Property(5, Unit1.A**2 / Unit2.B / Unit4.D)

    @args({"other": Property(0, Unit1.A**2)})
    def test_with_numerator_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(2, (Unit2.B * Unit4.D).inverse())})
    def test_with_denominator_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, (Unit1.A**2 / Unit2.B / Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "__sub__")
class TestPropertySubtractionWithUnregisteredUnitConverter(TestProperty):

    def build_property(self):
        return Property(2, Unit3.C)

    @args({"other": Property(6, Unit3.C)})
    def test_with_same_units(self):
        self.assert_result("-4 C")

    @args({"other": Property(3, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()


@add_to(property_test_suite, "__sub__")
class TestAliasPropertySubtraction(TestProperty):
    def build_property(self) -> Property:
        return Property(25, Unit8.H)

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assert_result("15.0 H")

    @args({"other": Property(15, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assert_result("10.0 H")

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assert_result("15.0 H")

    @args({"other": Property(500, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assert_result("15.0 H")


@add_to(property_test_suite, "__rsub__")
class TestSimplePropertyRightSubtraction(TestProperty):

    def build_property(self):
        return Property(2.5, Unit1.A)

    @args({"other": 99})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(2, Unit2.B)})
    def test_with_other_unit_type(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(6, Unit1.A)})
    def test_with_same_unit(self):
        self.assert_result("3.5 A")

    @args({"other": Property(20, Unit1.a)})
    def test_with_different_unit(self):
        self.assert_result("-5.0 a")

    @args({"other": -Property(2.5, Unit1.A)})
    def test_with_negative(self):
        self.assert_result("-5.0 A")


@add_to(property_test_suite, "__rsub__")
class TestAliasPropertyRightSubtraction(TestProperty):
    def build_property(self) -> Property:
        return Property(25, Unit8.H)

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assert_result("-60.0 (a^2) / (d^2)")

    @args({"other": Property(15, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assert_result("-10.0 (A^2) / (D^2)")

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assert_result("-60.0 f / (d^2)")


@add_to(property_test_suite, "__pow__")
class TestPropertyExponentiation(TestProperty):

    def build_property(self):
        return Property(4, Unit1.A)

    @args({"power": "3.2"})
    def test_with_invalid_value(self):
        self.assertResultRaises(PropertyExponentError)

    @args({"power": 2})
    def test_with_positive_value(self):
        self.assert_result("16 (A^2)")

    @args({"power": -2})
    def test_with_negative_value(self):
        self.assert_result("0.0625 (A^-2)")

    @args({"power": 0.5})
    def test_with_float(self):
        self.assert_result("2.0 (A^0.5)")


@add_to(property_test_suite, "__eq__")
class TestPropertyEquality(TestProperty):

    def build_property(self):
        return Property(-22.2, Unit1.A * Unit4.D)

    @args({"other": "1 A * B"})
    def test_with_str(self):
        self.assertResultFalse()

    @args({"other": -22.2})
    def test_with_numeric(self):
        self.assertResultFalse()

    @args({"other": Property(-22.2, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assertResultFalse()

    # this test will fail due to floating point equality
    @args({"other": Property(-222, Unit1.a * Unit4.D)})
    def test_with_other_units(self):
        self.assertResultFalse()

    @args({"other": Property(-22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assertResultFalse()

    @args({"other": Property(1, Unit1.A2 * Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(-22.2, Unit1.A * Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultTrue()

    # this test is false due to floating point inequality
    @args({"other": Property(-222, Unit1.a * Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultFalse()

    @args({"other": Property(22.2, Unit1.A * Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__eq__")
class TestPropertyWithUnregistedUnitsEquality(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(2, Unit3.C)})
    def test_with_unequal_value(self):
        self.assertResultFalse()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__ne__")
class TestPropertyInequality(TestProperty):

    def build_property(self):
        return Property(-22.2, Unit1.A * Unit4.D)

    @args({"other": "1 A * B"})
    def test_with_str(self):
        self.assertResultTrue()

    @args({"other": -22.2})
    def test_with_numeric(self):
        self.assertResultTrue()

    @args({"other": Property(-22.2, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assertResultTrue()

    # this test is True due to floating point inequality
    @args({"other": Property(-222, Unit1.a * Unit4.D)})
    def test_with_other_units(self):
        self.assertResultTrue()

    @args({"other": Property(-22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assertResultTrue()

    @args({"other": Property(1, Unit1.A2 * Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(-22.2, Unit1.A * Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultFalse()

    # this test is true due to floating point inequality
    @args({"other": Property(-222, Unit1.a * Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultTrue()

    @args({"other": Property(22.2, Unit1.A * Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__ne__")
class TestPropertyWithUnregistedUnitsInequality(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(2, Unit3.C)})
    def test_with_unequal_value(self):
        self.assertResultTrue()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__gt__")
class TestPropertyGreater(TestProperty):

    def build_property(self) -> Property:
        return Property(12, Unit1.A / Unit4.D)

    @args({"other": 4})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(20, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assert_invalid_operation()

    @args({"other": Property(130, Unit1.a / Unit4.D)})
    def test_with_other_units(self):
        self.assertResultFalse()

    @args({"other": Property(22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2 / Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(12, Unit1.A / Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultFalse()

    @args({"other": Property(120, Unit1.a / Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultFalse()

    @args({"other": Property(-12, Unit1.A / Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultTrue()

    @args({"other": Property(13, Unit1.A / Unit4.D)})
    def test_with_bigger_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__gt__")
class TestPropertyWithUnregistedUnitsGreater(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(6, Unit3.C)})
    def test_with_bigger_value(self):
        self.assertResultFalse()

    @args({"other": Property(3, Unit3.C)})
    def test_with_smaller_value(self):
        self.assertResultTrue()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__gt__")
class TestAliasPropertyGreater(TestProperty):
    def build_property(self):
        return Property(10, Unit8.H)

    @args({"other": Property(35, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(15, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assertResultFalse()

    @args({"other": Property(22, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(345, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__ge__")
class TestPropertyGreaterEqual(TestProperty):

    def build_property(self) -> Property:
        return Property(12, Unit1.A * Unit4.D)

    @args({"other": 4})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(20, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assert_invalid_operation()

    @args({"other": Property(13 * 10 * 5, Unit1.a * Unit4.d)})
    def test_with_other_units(self):
        self.assertResultFalse()

    @args({"other": Property(22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2 * Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(12, Unit1.A * Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultTrue()

    @args({"other": Property(120, Unit1.a * Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultTrue()

    @args({"other": Property(-12, Unit1.A * Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultTrue()

    @args({"other": Property(13, Unit1.A * Unit4.D)})
    def test_with_bigger_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__ge__")
class TestPropertyWithUnregistedUnitsGreaterEqual(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(6, Unit3.C)})
    def test_with_bigger_value(self):
        self.assertResultFalse()

    @args({"other": Property(3, Unit3.C)})
    def test_with_smaller_value(self):
        self.assertResultTrue()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__ge__")
class TestAliasPropertyGreaterEqual(TestProperty):
    def build_property(self):
        return Property(10, Unit8.H)

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(20, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assertResultFalse()

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(500, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__lt__")
class TestPropertyLower(TestProperty):

    def build_property(self) -> Property:
        return Property(15, Unit1.A * Unit4.D)

    @args({"other": 4})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(20, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assert_invalid_operation()

    @args({"other": Property(13 * 10 * 5, Unit1.a * Unit4.d)})
    def test_with_other_units(self):
        self.assertResultFalse()

    @args({"other": Property(22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2 * Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(15, Unit1.A * Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultFalse()

    @args({"other": Property(15 * 10, Unit1.a * Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultFalse()

    @args({"other": Property(-15, Unit1.A * Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultFalse()

    @args({"other": Property(23, Unit1.A * Unit4.D)})
    def test_with_bigger_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__lt__")
class TestPropertyWithUnregistedUnitsLower(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(6, Unit3.C)})
    def test_with_bigger_value(self):
        self.assertResultTrue()

    @args({"other": Property(3, Unit3.C)})
    def test_with_smaller_value(self):
        self.assertResultFalse()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultFalse()


@add_to(property_test_suite, "__lt__")
class TestAliasPropertyLower(TestProperty):
    def build_property(self):
        return Property(10, Unit8.H)

    @args({"other": Property(50, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(11, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assertResultTrue()

    @args({"other": Property(20, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assertResultFalse()

    @args({"other": Property(600, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__le__")
class TestPropertyLowerEqual(TestProperty):

    def build_property(self) -> Property:
        return Property(15, Unit1.A * Unit4.D)

    @args({"other": 4})
    def test_with_numeric(self):
        self.assert_invalid_operation()

    @args({"other": Property(20, Unit1.A)})
    def test_with_other_unit_type(self):
        self.assert_invalid_operation()

    @args({"other": Property(13 * 10 * 5, Unit1.a * Unit4.d)})
    def test_with_other_units(self):
        self.assertResultFalse()

    @args({"other": Property(22.2, (Unit1.A * Unit4.D).inverse())})
    def test_with_inverse_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(1, Unit1.A2 * Unit4.D)})
    def test_with_unregistered_unit(self):
        self.assert_invalid_operation()

    @args({"other": Property(15, Unit1.A * Unit4.D)})
    def test_with_same_prop(self):
        self.assertResultTrue()

    @args({"other": Property(150, Unit1.a * Unit4.D)})
    def test_with_other_units_same_value(self):
        self.assertResultTrue()

    @args({"other": Property(-15, Unit1.A * Unit4.D)})
    def test_with_negative_prop(self):
        self.assertResultFalse()

    @args({"other": Property(23, Unit1.A * Unit4.D)})
    def test_with_bigger_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__le__")
class TestPropertyWithUnregistedUnitsLowerEqual(TestProperty):

    def build_property(self):
        return Property(5, Unit3.C)

    @args({"other": Property(6, Unit3.C)})
    def test_with_bigger_value(self):
        self.assertResultTrue()

    @args({"other": Property(3, Unit3.C)})
    def test_with_smaller_value(self):
        self.assertResultFalse()

    @args({"other": Property(50, Unit3.c)})
    def test_with_other_units(self):
        self.assert_invalid_operation()

    @args({"other": Property(5, Unit3.C)})
    def test_with_same_prop(self):
        self.assertResultTrue()


@add_to(property_test_suite, "__le__")
class TestAliasPropertyLowerEqual(TestProperty):
    def build_property(self):
        return Property(10, Unit8.H)

    @args({"other": Property(40, Unit1.a**2 / Unit4.d**2)})
    def test_with_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(11, Unit1.A**2 / Unit4.D**2)})
    def test_with_aliased_units(self):
        self.assertResultTrue()

    @args({"other": Property(40, Unit6.f / Unit4.d**2)})
    def test_with_other_aliased_si_units(self):
        self.assertResultTrue()

    @args({"other": Property(505, Unit6.F / Unit4.D**2)})
    def test_with_other_aliased_units(self):
        self.assertResultTrue()
