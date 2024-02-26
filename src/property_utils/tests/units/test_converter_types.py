from unittest import TestSuite, TextTestRunner

from unittest_extensions import TestCase, args


from property_utils.units.converter_types import (
    get_converter,
    register_converter,
)
from property_utils.exceptions.base import (
    PropertyUtilsTypeError,
    PropertyUtilsValueError,
)
from property_utils.exceptions.units.converter_types import (
    UndefinedConverterError,
    UnitConversionError,
    ConversionFunctionError,
    ConverterDependenciesError,
    UnsupportedConverterError,
)
from property_utils.tests.utils import add_to, def_load_tests
from property_utils.tests.data import (
    Unit1,
    Unit2,
    Unit3,
    Unit4,
    Unit1Converter,
    UnregisteredConverter,
    Unit1_314Converter,
    Unit2_4Converter,
    Unit3_2Converter,
    Unit2Converter,
    Unit1Unit4Converter,
    Unit1Unit3Converter,
    Unit1Unit2Converter,
    Unit1Unit4FractionConverter,
    Unit1_2Unit4_3Converter,
)


load_tests = def_load_tests("property_utils.units.converter_types")


converter_types_test_suite = TestSuite()

converter_types_test_suite.addTests(
    [
        (GetConverter_test_suite := TestSuite()),
        (RegisterConverter_test_suite := TestSuite()),
        (AbsoluteUnitConverter_test_suite := TestSuite()),
        (RelativeUnitConverter_test_suite := TestSuite()),
        (ExponentiatedUnitConverter_test_suite := TestSuite()),
        (CompositeUnitConverter_test_suite := TestSuite()),
    ]
)


@add_to(GetConverter_test_suite)
class TestGetConverter(TestCase):
    def subject(self, generic):
        return get_converter(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(PropertyUtilsTypeError)

    @args({"generic": Unit3})
    def test_with_unregistered_generic(self):
        self.assertResultRaises(UndefinedConverterError)

    @args({"generic": Unit2})
    def test_with_measurement_unit_type(self):
        self.assertResult(Unit2Converter)

    @args({"generic": Unit1**1})
    def test_with_equivalent_generic_dimension(self):
        self.assertResult(Unit1Converter)

    @args({"generic": Unit1**3.14})
    def test_with_generic_dimension(self):
        self.assertResult(Unit1_314Converter)

    @args({"generic": Unit1 * Unit4})
    def test_with_generic_composite_dimension(self):
        self.assertResult(Unit1Unit4Converter)


@add_to(RegisterConverter_test_suite)
class TestRegisterConverter(TestCase):
    def subject(self, generic):
        return register_converter(generic)(UnregisteredConverter)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(PropertyUtilsTypeError)

    @args({"generic": Unit1})
    def test_with_registered_converter(self):
        self.assertResultRaises(PropertyUtilsValueError)

    @args({"generic": Unit3})
    def test_with_unregistered_converter(self):
        self.assertResult(UnregisteredConverter)
        self.assertEqual(self.cachedResult().generic_unit_descriptor, Unit3)


@add_to(AbsoluteUnitConverter_test_suite)
class TestAbsoluteUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1Converter.convert(value, from_descriptor, to_descriptor)

    @args({"value": "12.34", "from_descriptor": Unit1.A, "to_descriptor": Unit1.a})
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 10, "from_descriptor": Unit2.B, "to_descriptor": Unit1.A})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 2, "from_descriptor": Unit1.A, "to_descriptor": Unit2.b})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 5, "from_descriptor": Unit1.A2, "to_descriptor": Unit1.A})
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 9, "from_descriptor": Unit1.A, "to_descriptor": Unit1.A2})
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 10.1, "from_descriptor": Unit1.A, "to_descriptor": Unit1.a})
    def test_valid_conversion_from_A_to_a(self):
        self.assertResult(101)

    @args({"value": 200, "from_descriptor": Unit1.a, "to_descriptor": Unit1.A})
    def test_valid_conversion_from_a_to_A(self):
        self.assertResult(20)


@add_to(AbsoluteUnitConverter_test_suite)
class TestAbsoluteUnitConverterGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit1Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit2.B, "to_descriptor": Unit1.A})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.a, "to_descriptor": Unit2.B})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A2, "to_descriptor": Unit1.A})
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A, "to_descriptor": Unit1.A2})
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A, "to_descriptor": Unit1.a})
    def test_from_A_to_a(self):
        self.assertResult(10)

    @args({"from_descriptor": Unit1.a, "to_descriptor": Unit1.A})
    def test_from_a_to_A(self):
        self.assertResult(0.1)


@add_to(RelativeUnitConverter_test_suite)
class TestRelativeUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit2Converter.convert(value, from_descriptor, to_descriptor)

    @args({"value": "0.98", "from_descriptor": Unit2.B, "to_descriptor": Unit2.B})
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 12, "from_descriptor": Unit1.A, "to_descriptor": Unit2.B})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 9, "from_descriptor": Unit2.B, "to_descriptor": Unit1.A})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 5, "from_descriptor": Unit2.B2, "to_descriptor": Unit2.B})
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 4, "from_descriptor": Unit2.B, "to_descriptor": Unit2.B2})
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 10, "from_descriptor": Unit2.B3, "to_descriptor": Unit2.B})
    def test_from_descriptor_with_erroneous_conversion_function(self):
        self.assertResultRaises(ConversionFunctionError)

    @args({"value": 0, "from_descriptor": Unit2.B, "to_descriptor": Unit2.B3})
    def test_to_descriptor_with_erroneous_conversion_function(self):
        self.assertResultRaises(ConversionFunctionError)

    @args({"value": 10, "from_descriptor": Unit2.B, "to_descriptor": Unit2.b})
    def test_from_B_to_b(self):
        self.assertResult(3.5)

    @args({"value": 10, "from_descriptor": Unit2.b, "to_descriptor": Unit2.B})
    def test_from_b_to_B(self):
        self.assertResult(23)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestExponentiatedUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1_314Converter.convert(value, from_descriptor, to_descriptor)

    @args(
        {"value": "1", "from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.A**3.14}
    )
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 9, "from_descriptor": Unit1.A**2, "to_descriptor": Unit1.A**3.14})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 2, "from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.A})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {"value": -1, "from_descriptor": Unit1.A2**3.14, "to_descriptor": Unit1.A**3.14}
    )
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {"value": 5, "from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.A2**3.14}
    )
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {"value": 7, "from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.a**3.14}
    )
    def test_valid_conversion_from_A314_to_a314(self):
        self.assertResult(7 * (10**3.14))

    @args(
        {"value": 3, "from_descriptor": Unit1.a**3.14, "to_descriptor": Unit1.A**3.14}
    )
    def test_valid_conversion_from_a314_to_A314(self):
        self.assertResultAlmost(3 * (10 ** (-3.14)), 3)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestExponentiatedUnitConverterWithMissingDependenciesConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit3_2Converter.convert(value, from_descriptor, to_descriptor)

    @args({"value": "abs", "from_descriptor": Unit3.C**2, "to_descriptor": Unit3.c**2})
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 45, "from_descriptor": Unit2.B**2, "to_descriptor": Unit3.C**2})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 12, "from_descriptor": Unit3.c**2, "to_descriptor": Unit2.B**2})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 5, "from_descriptor": Unit3.C**2, "to_descriptor": Unit3.c**2})
    def test_from_C_to_c(self):
        self.assertResultRaises(ConverterDependenciesError)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestUnsupportedExponentiatedUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit2_4Converter.convert(value, from_descriptor, to_descriptor)

    @args({"value": "plk", "from_descriptor": Unit2.B**4, "to_descriptor": Unit2.b**4})
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 15, "from_descriptor": Unit1.A**4, "to_descriptor": Unit2.b**4})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 4, "from_descriptor": Unit2.B**4, "to_descriptor": Unit1.A**4})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"value": 6, "from_descriptor": Unit2.B**4, "to_descriptor": Unit2.b**4})
    def test_from_B_to_b(self):
        self.assertResultRaises(UnsupportedConverterError)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestExponentiatedUnitConverterGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit1_314Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit2.B**3.14, "to_descriptor": Unit1.A**3.14})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.a**3.14, "to_descriptor": Unit2.B**3.14})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A2**3.14, "to_descriptor": Unit1.A**3.14})
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.A2**3.14})
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A**3.14, "to_descriptor": Unit1.a**3.14})
    def test_from_A_to_a(self):
        self.assertResult(10**3.14)

    @args({"from_descriptor": Unit1.a**3.14, "to_descriptor": Unit1.A**3.14})
    def test_from_a_to_A(self):
        self.assertResultAlmost(10 ** (-3.14), 3)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestExponentiatedUnitConverterWithMissingDependenciesGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit3_2Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit2.B**2, "to_descriptor": Unit3.C**2})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit3.c**2, "to_descriptor": Unit2.B**2})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit3.C**2, "to_descriptor": Unit3.c**2})
    def test_from_C_to_c(self):
        self.assertResultRaises(ConverterDependenciesError)


@add_to(ExponentiatedUnitConverter_test_suite)
class TestUnsupportedExponentiatedUnitConverterGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit2_4Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit1.A**4, "to_descriptor": Unit2.b**4})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit2.B**4, "to_descriptor": Unit1.A**4})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit2.B**4, "to_descriptor": Unit2.b**4})
    def test_from_B_to_b(self):
        self.assertResultRaises(UnsupportedConverterError)


@add_to(CompositeUnitConverter_test_suite)
class TestCompositeUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1Unit4Converter.convert(value, from_descriptor, to_descriptor)

    @args(
        {
            "value": "0.1",
            "from_descriptor": Unit1.A * Unit2.B,
            "to_descriptor": Unit1.a * Unit4.d,
        }
    )
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 1,
            "from_descriptor": Unit3.C * Unit2.B,
            "to_descriptor": Unit1.A * Unit4.D,
        }
    )
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 7,
            "from_descriptor": Unit1.A * Unit4.D,
            "to_descriptor": Unit3.C * Unit1.A,
        }
    )
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 6,
            "from_descriptor": Unit1.A2 * Unit4.D,
            "to_descriptor": Unit1.A * Unit4.D,
        }
    )
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 2,
            "from_descriptor": Unit1.A * Unit4.D,
            "to_descriptor": Unit1.A * Unit4.D2,
        }
    )
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 5,
            "from_descriptor": Unit1.A * Unit4.D,
            "to_descriptor": Unit1.a * Unit4.d,
        }
    )
    def test_valid_conversion_from_AD_to_ad(self):
        self.assertResult(250)

    @args(
        {
            "value": 100,
            "from_descriptor": Unit1.a * Unit4.d,
            "to_descriptor": Unit1.A * Unit4.D,
        }
    )
    def test_valid_conversion_from_ad_to_AD(self):
        self.assertResultAlmost(2, 3)

    @args(
        {
            "value": 15,
            "from_descriptor": Unit1.A * Unit4.D,
            "to_descriptor": Unit4.D * Unit1.A,
        }
    )
    def test_from_AD_to_DA(self):
        self.assertResult(15)


@add_to(CompositeUnitConverter_test_suite)
class TestCompositeUnitConverterWithMissingDependenciesConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1Unit3Converter.convert(value, from_descriptor, to_descriptor)

    @args(
        {
            "value": "0.1",
            "from_descriptor": Unit1.A * Unit3.C,
            "to_descriptor": Unit1.a * Unit3.c,
        }
    )
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 1,
            "from_descriptor": Unit1.A * Unit2.B,
            "to_descriptor": Unit1.A * Unit3.C,
        }
    )
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 7,
            "from_descriptor": Unit1.A * Unit3.C,
            "to_descriptor": Unit1.A * Unit2.B,
        }
    )
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 1,
            "from_descriptor": Unit1.A * Unit3.C,
            "to_descriptor": Unit1.a * Unit3.c,
        }
    )
    def test_from_AC_to_ac(self):
        self.assertResultRaises(ConverterDependenciesError)


@add_to(CompositeUnitConverter_test_suite)
class TestUnsupportedCompositeUnitConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1Unit2Converter.convert(value, from_descriptor, to_descriptor)

    @args(
        {
            "value": "0.1",
            "from_descriptor": Unit1.A * Unit2.B,
            "to_descriptor": Unit1.a * Unit2.b,
        }
    )
    def test_with_invalid_value(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 1,
            "from_descriptor": Unit1.A * Unit3.C,
            "to_descriptor": Unit1.A * Unit2.B,
        }
    )
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 7,
            "from_descriptor": Unit1.A * Unit2.B,
            "to_descriptor": Unit1.A * Unit3.C,
        }
    )
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args(
        {
            "value": 1,
            "from_descriptor": Unit1.A * Unit2.B,
            "to_descriptor": Unit1.a * Unit2.b,
        }
    )
    def test_from_AB_to_ab(self):
        self.assertResultRaises(UnsupportedConverterError)


@add_to(CompositeUnitConverter_test_suite)
class TestFractionCompositeConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1Unit4FractionConverter.convert(
            value, from_descriptor, to_descriptor
        )

    @args(
        {
            "value": 25,
            "from_descriptor": Unit1.A / Unit4.D,
            "to_descriptor": Unit1.a / Unit4.d,
        }
    )
    def test_valid_conversion_from_AD_to_ad(self):
        self.assertResult(50)

    @args(
        {
            "value": 20,
            "from_descriptor": Unit1.a / Unit4.d,
            "to_descriptor": Unit1.A / Unit4.D,
        }
    )
    def test_valid_conversion_from_ad_to_AD(self):
        self.assertResult(10)


@add_to(CompositeUnitConverter_test_suite)
class TestComplexCompositeConverterConvert(TestCase):
    def subject(self, value, from_descriptor, to_descriptor):
        return Unit1_2Unit4_3Converter.convert(value, from_descriptor, to_descriptor)

    @args(
        {
            "value": 10,
            "from_descriptor": (Unit1.A**2 / Unit4.D**3),
            "to_descriptor": (Unit1.a**2 / Unit4.d**3),
        }
    )
    def test_valid_conversion_from_A2D3_to_a2d3(self):
        self.assertResult(10 / 1.25)

    @args(
        {
            "value": 10,
            "from_descriptor": (Unit1.A**2 / Unit4.D**3),
            "to_descriptor": (Unit1.a**2 / Unit4.D**3),
        }
    )
    def test_valid_conversion_from_A2D3_to_a2D3(self):
        self.assertResult(1000)

    @args(
        {
            "value": 10,
            "from_descriptor": (Unit1.A**2 / Unit4.D**3),
            "to_descriptor": (Unit1.A**2 / Unit4.d**3),
        }
    )
    def test_valid_conversion_from_A2D3_to_A2d3(self):
        self.assertResult(10 / 125)


@add_to(CompositeUnitConverter_test_suite)
class TestCompositeUnitConverterGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit1Unit4Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit3.C * Unit2.B, "to_descriptor": Unit1.A * Unit4.D})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit4.D, "to_descriptor": Unit3.C * Unit1.A})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A2 * Unit4.D, "to_descriptor": Unit1.A * Unit4.D})
    def test_with_unregistered_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit4.D, "to_descriptor": Unit1.A * Unit4.D2})
    def test_with_unregistered_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit4.D, "to_descriptor": Unit1.a * Unit4.d})
    def test_valid_conversion_from_AD_to_ad(self):
        self.assertResult(50)

    @args({"from_descriptor": Unit1.a * Unit4.d, "to_descriptor": Unit1.A * Unit4.D})
    def test_valid_conversion_from_ad_to_AD(self):
        self.assertResultAlmost(0.02, 3)

    @args({"from_descriptor": Unit1.A * Unit4.D, "to_descriptor": Unit4.D * Unit1.A})
    def test_from_AD_to_DA(self):
        self.assertResult(1)


@add_to(CompositeUnitConverter_test_suite)
class TestCompositeUnitConverterWithMissingDependenciesGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit1Unit3Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit1.A * Unit2.B, "to_descriptor": Unit1.A * Unit3.C})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit3.C, "to_descriptor": Unit1.A * Unit2.B})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit3.C, "to_descriptor": Unit1.a * Unit3.c})
    def test_from_AC_to_ac(self):
        self.assertResultRaises(ConverterDependenciesError)


@add_to(CompositeUnitConverter_test_suite)
class TestUnsupportedCompositeUnitConverterGetFactor(TestCase):
    def subject(self, from_descriptor, to_descriptor):
        return Unit1Unit2Converter.get_factor(from_descriptor, to_descriptor)

    @args({"from_descriptor": Unit1.A * Unit3.C, "to_descriptor": Unit1.A * Unit2.B})
    def test_with_invalid_from_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit2.B, "to_descriptor": Unit1.A * Unit3.C})
    def test_with_invalid_to_descriptor(self):
        self.assertResultRaises(UnitConversionError)

    @args({"from_descriptor": Unit1.A * Unit2.B, "to_descriptor": Unit1.a * Unit2.b})
    def test_from_AB_to_ab(self):
        self.assertResultRaises(UnsupportedConverterError)


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(converter_types_test_suite)
