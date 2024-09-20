from typing import Any
from unittest import TestSuite, TextTestRunner
from operator import mul, truediv

from unittest_extensions import args
from typing_extensions import override

from property_utils.units.descriptors import (
    MeasurementUnit,
    AliasMeasurementUnit,
    Dimension,
    CompositeDimension,
    GenericDimension,
    GenericCompositeDimension,
)
from property_utils.exceptions.units.descriptors import (
    DescriptorExponentError,
    UnitDescriptorTypeError,
)
from property_utils.tests.utils import add_to, def_load_tests, ids
from property_utils.tests.units.descriptors_utils import (
    TestDescriptor,
    TestDescriptorBinaryOperation,
)
from property_utils.tests.data import (
    Unit1,
    Unit2,
    Unit3,
    Unit5,
    Unit6,
    Unit7,
    dimension_1,
    dimension_2,
    dimension_3,
    dimension_4,
    dimension_5,
    dimension_6,
    dimension_7,
    generic_dimension_1,
    generic_dimension_2,
    generic_dimension_3,
    generic_dimension_4,
    generic_dimension_5,
    generic_dimension_6,
    generic_dimension_7,
    composite_dimension,
    generic_composite_dimension,
)


load_tests = def_load_tests("property_utils.units.descriptors")


descriptors_test_suite = TestSuite()

descriptors_test_suite.addTests(
    [
        (MeasurementUnitMeta_test_suite := TestSuite()),
        (MeasurementUnit_test_suite := TestSuite()),
        (AliasMeasurementUnit_test_suite := TestSuite()),
        (GenericDimension_test_suite := TestSuite()),
        (Dimension_test_suite := TestSuite()),
        (GenericCompositeDimension_test_suite := TestSuite()),
        (CompositeDimension_test_suite := TestSuite()),
    ]
)


@add_to(MeasurementUnitMeta_test_suite)
class TestMeasurementUnitMetaInverseGeneric(TestDescriptor):
    def test_inverse_generic(self):
        self.assertSequenceEqual(str(Unit1.inverse_generic()), " / Unit1", str)


@add_to(MeasurementUnitMeta_test_suite)
class TestMeasurementUnitMetaMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit1

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result(
            "(Unit1^2) * Unit1 * Unit2 / (Unit3^3)",
        )

    @args({"descriptor": generic_dimension_1(2)})
    def test_with_generic_dimension(self):
        self.assert_result("(Unit1^2) * Unit1")

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("Unit1 * Unit2")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": 100})
    def test_with_int(self):
        self.assert_invalid()


@add_to(MeasurementUnitMeta_test_suite)
class TestMeasurementUnitMetaDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit1

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result("(Unit3^3) * Unit1 / (Unit1^2) / Unit2")

    @args({"descriptor": generic_dimension_2(3.14)})
    def test_with_generic_dimension(self):
        self.assert_result("Unit1 / (Unit2^3.14)")

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("Unit1 / Unit2")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": 23})
    def test_with_int(self):
        self.assert_invalid()


@add_to(MeasurementUnitMeta_test_suite)
class TestMeasurementUnitMetaExponentiation(TestDescriptor):
    produced_type = GenericDimension

    def subject(self, value):
        return Unit1**value

    @args({"value": 3})
    def test_with_int(self):
        self.assert_result("(Unit1^3)")

    @args({"value": -7})
    def test_with_negative_int(self):
        self.assert_result("(Unit1^-7)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(Unit1^0)")

    @args({"value": 1.728})
    def test_with_float(self):
        self.assert_result("(Unit1^1.728)")

    @args({"value": -0.091})
    def test_with_negative_float(self):
        self.assert_result("(Unit1^-0.091)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(MeasurementUnitMeta_test_suite)
class TestMeasurementUnitMetaIsEquivalent(TestDescriptor):
    def subject(self, descriptor):
        return Unit3.is_equivalent(descriptor)

    @args({"descriptor": generic_dimension_1(3)})
    def test_with_aliased_unit(self):
        self.assertResultTrue()

    @args({"descriptor": Unit3})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"descriptor": generic_dimension_3()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"descriptor": generic_dimension_3(2)})
    def test_with_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"descriptor": GenericCompositeDimension([generic_dimension_3()])})
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args({"descriptor": GenericCompositeDimension([generic_dimension_1(3)])})
    def test_with_alias_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "descriptor": GenericCompositeDimension(
                [generic_dimension_3()], [generic_dimension_1()]
            )
        }
    )
    def test_with_generic_composite_dimension_same_numerator(self):
        self.assertResultFalse()


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitFromDescriptor(TestDescriptor):
    def subject(self, descriptor):
        return MeasurementUnit.from_descriptor(descriptor)

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assertResult(Unit2.B)

    def test_returns_same_object(self):
        descriptor = Unit2.B
        self.assertIs(descriptor, MeasurementUnit.from_descriptor(descriptor))

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResult(Unit1.A)

    @args({"descriptor": dimension_1(5)})
    def test_with_exponentiated_dimension(self):
        self.assertResult(Unit1.A)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitIsInstance(TestDescriptor):
    def subject(self, generic):
        return Unit1.A.isinstance(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_correct_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": Unit2})
    def test_with_wrong_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitIsInstanceEquivalent(TestDescriptor):
    def subject(self, descriptor):
        return Unit3.C.isinstance_equivalent(descriptor)

    @args({"descriptor": generic_dimension_1(3)})
    def test_with_aliased_unit(self):
        self.assertResultTrue()

    @args({"descriptor": Unit3})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"descriptor": generic_dimension_3()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"descriptor": generic_dimension_3(2)})
    def test_with_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"descriptor": GenericCompositeDimension([generic_dimension_3()])})
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args({"descriptor": GenericCompositeDimension([generic_dimension_1(3)])})
    def test_with_alias_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "descriptor": GenericCompositeDimension(
                [generic_dimension_3()], [generic_dimension_1()]
            )
        }
    )
    def test_with_generic_composite_dimension_same_numerator(self):
        self.assertResultFalse()


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitToGeneric(TestDescriptor):
    def test_to_generic(self):
        self.assertEqual(Unit1.A.to_generic(), Unit1)


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitInverse(TestDescriptor):
    def test_inverse(self):
        self.assertSequenceEqual(str(Unit1.A.inverse()), " / A", str)


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = CompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit1.A

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_result("A * B")

    @args({"descriptor": Unit1.A})
    def test_with_same_measurement_unit(self):
        self.assert_result("A * A")

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_result("A * B")

    @args({"descriptor": dimension_2(2.3)})
    def test_with_exponentiated_dimension(self):
        self.assert_result("(B^2.3) * A")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * A * B / (C^3)")

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": 78})
    def test_with_int(self):
        self.assert_invalid()


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = CompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit1.A

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_result("A / B")

    @args({"descriptor": Unit1.A})
    def test_with_same_measurement_unit(self):
        self.assert_result("A / A")

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_result("A / B")

    @args({"descriptor": dimension_2(-2.1)})
    def test_with_exponentiated_dimension(self):
        self.assert_result("A / (B^-2.1)")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(C^3) * A / (A^2) / B")

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_2()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": 0})
    def test_with_int(self):
        self.assert_invalid()


@add_to(MeasurementUnit_test_suite)
class TestMeasurementUnitExponentiation(TestDescriptor):
    produced_type = Dimension

    def subject(self, value):
        return Unit1.A**value

    @args({"value": 1298})
    def test_with_int(self):
        self.assert_result("(A^1298)")

    @args({"value": -23})
    def test_with_negative_int(self):
        self.assert_result("(A^-23)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(A^0)")

    @args({"value": 0.1065})
    def test_with_float(self):
        self.assert_result("(A^0.1065)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitFromDescriptor(TestDescriptor):
    def subject(self, descriptor):
        return AliasMeasurementUnit.from_descriptor(descriptor)

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": Unit3.C})
    def test_with_aliased_measurement_unit(self):
        self.assertResult(Unit3.C)

    def test_returns_same_object(self):
        descriptor = Unit3.C
        self.assertIs(descriptor, AliasMeasurementUnit.from_descriptor(descriptor))

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": dimension_3()})
    def test_with_aliased_dimension(self):
        self.assertResult(Unit3.C)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitIsInstance(TestDescriptor):
    def subject(self, generic):
        return Unit5.E.isinstance(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": Unit5})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_aliased_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_3()})
    def test_with_aliased_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitToGeneric(TestDescriptor):
    def test_to_generic(self):
        self.assertEqual(Unit3.C.to_generic(), Unit3)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = CompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit3.C

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_result("B * C")

    @args({"descriptor": Unit3.C})
    def test_with_aliased_measurement_unit(self):
        self.assert_result("C * C")

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_result("A * C")

    @args({"descriptor": dimension_3()})
    def test_with_aliased_dimension(self):
        self.assert_result("C * C")

    @args({"descriptor": dimension_2(2.9)})
    def test_with_exponentiated_dimension(self):
        self.assert_result("(B^2.9) * C")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * B * C / (C^3)")

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": -99})
    def test_with_int(self):
        self.assert_invalid()


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = CompositeDimension

    @classmethod
    def build_descriptor(cls):
        return Unit3.C

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_result("C / B")

    @args({"descriptor": Unit3.C})
    def test_with_aliased_measurement_unit(self):
        self.assert_result("C / C")

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_result("C / A")

    @args({"descriptor": dimension_3()})
    def test_with_aliased_dimension(self):
        self.assert_result("C / C")

    @args({"descriptor": dimension_2(5)})
    def test_with_exponentiated_dimension(self):
        self.assert_result("C / (B^5)")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(C^3) * C / (A^2) / B")

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": 9})
    def test_with_int(self):
        self.assert_invalid()


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitExponentiation(TestDescriptor):
    produced_type = Dimension

    def subject(self, value):
        return Unit3.C**value

    @args({"value": 1298})
    def test_with_int(self):
        self.assert_result("(C^1298)")

    @args({"value": -23})
    def test_with_negative_int(self):
        self.assert_result("(C^-23)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(C^0)")

    @args({"value": 0.1065})
    def test_with_float(self):
        self.assert_result("(C^0.1065)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitInverse(TestDescriptor):
    def test_inverse(self):
        self.assertSequenceEqual(str(Unit3.C.inverse()), " / C")


@add_to(GenericDimension_test_suite)
class TestGenericDimensionToSi(TestDescriptor):
    produced_type = Dimension

    def subject(self, descriptor):
        return descriptor.to_si()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_result("a")

    @args({"descriptor": generic_dimension_1(2.3)})
    def test_with_exponentiated_generic_dimension(self):
        self.assert_result("(a^2.3)")


@add_to(GenericCompositeDimension_test_suite)
class TestGenericDimensionInverseGeneric(TestDescriptor):
    def test_inverse_generic(self):
        self.assertSequenceEqual(
            str(generic_dimension_1(2).inverse_generic()), " / (Unit1^2)", str
        )

    def test_object_is_not_persisted(self):
        generic = generic_dimension_1()
        composite = generic.inverse_generic()
        self.assertIsNot(composite.denominator[0], generic)


@add_to(GenericDimension_test_suite)
class TestGenericDimensionMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return generic_dimension_1()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("Unit1 * Unit2")

    @args({"descriptor": Unit3})
    def test_with_aliased_measurement_unit_type(self):
        self.assert_result("Unit1 * Unit3")

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_result("Unit1 * Unit1")

    @args({"descriptor": generic_dimension_2(-0.9)})
    def test_with_exponentiated_generic_dimension(self):
        self.assert_result("(Unit2^-0.9) * Unit1")

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result("(Unit1^2) * Unit1 * Unit2 / (Unit3^3)")

    @args({"descriptor": 12})
    def test_with_int(self):
        self.assert_invalid()


@add_to(GenericDimension_test_suite)
class TestGenericDimensionDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return generic_dimension_1()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("Unit1 / Unit2")

    @args({"descriptor": Unit3})
    def test_with_aliased_measurement_unit_type(self):
        self.assert_result("Unit1 / Unit3")

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_result("Unit1 / Unit1")

    @args({"descriptor": generic_dimension_2(-2)})
    def test_with_exponentiated_generic_dimension(self):
        self.assert_result("Unit1 / (Unit2^-2)")

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result("(Unit3^3) * Unit1 / (Unit1^2) / Unit2")

    @args({"descriptor": 12})
    def test_with_int(self):
        self.assert_invalid()


@add_to(GenericDimension_test_suite)
class TestGenericDimensionExponentiation(TestDescriptor):
    produced_type = GenericDimension

    def subject(self, value):
        return generic_dimension_1() ** value

    @args({"value": 18})
    def test_with_int(self):
        self.assert_result("(Unit1^18)")

    @args({"value": -3})
    def test_with_negative_int(self):
        self.assert_result("(Unit1^-3)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(Unit1^0)")

    @args({"value": 0.2648})
    def test_with_float(self):
        self.assert_result("(Unit1^0.2648)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(GenericCompositeDimension_test_suite)
class TestExponentiatedGenericDimensionExponentiation(TestDescriptor):
    produced_type = GenericDimension

    def subject(self, value):
        return generic_dimension_1(3) ** value

    @args({"value": 8})
    def test_with_int(self):
        self.assert_result("(Unit1^24)")

    @args({"value": -3})
    def test_with_negative_int(self):
        self.assert_result("(Unit1^-9)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(Unit1^0)")

    @args({"value": 0.25})
    def test_with_float(self):
        self.assert_result("(Unit1^0.75)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(GenericDimension_test_suite)
class TestGenericDimensionEquality(TestDescriptor):
    def subject(self, generic):
        return generic_dimension_1() == generic

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_1(2)})
    def test_with_same_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": GenericCompositeDimension([generic_dimension_1()])})
    def test_with_numerator_generic_composite_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_2()]
            )
        }
    )
    def test_with_generic_composite_dimension_same_numerator(self):
        self.assertResultFalse()


@add_to(GenericDimension_test_suite)
class TestGenericDimensionIsEquivalent(TestGenericDimensionEquality):
    """
    Run all tests in TestGenericDimensionEquality but with different subject.
    """

    def subject(self, generic):
        return generic_dimension_1().is_equivalent(generic)

    @override
    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @override
    @args({"generic": GenericCompositeDimension([generic_dimension_1()])})
    def test_with_numerator_generic_composite_dimension(self):
        self.assertResultTrue()


@add_to(GenericDimension_test_suite)
class TestExponentiatedGenericDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic):
        return generic_dimension_1(3).is_equivalent(generic)

    @args({"generic": generic_dimension_1(3)})
    def test_with_same_generic(self):
        return self.assertResultTrue()

    @args({"generic": Unit3})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3()})
    def test_with_alias_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3(2)})
    def test_with_exponentiated_alias_dimension(self):
        self.assertResultFalse()


@add_to(GenericDimension_test_suite)
class TestAliasGenericDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic, power=1):
        return generic_dimension_3(power).is_equivalent(generic)

    @args({"generic": generic_dimension_1(3)})
    def test_with_aliased_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_6(3), "power": 2})
    def test_with_other_alias_generic_dimension(self):
        self.assertResultTrue()


@add_to(GenericDimension_test_suite)
class TestComplexAliasGenericDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic, power=1):
        return generic_dimension_5(power).is_equivalent(generic)

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_aliased_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_4(4)]
            ),
            "power": 2,
        }
    )
    def test_with_exponentiated_aliased_composite_dimension(self):
        self.assertResultTrue()


@add_to(Dimension_test_suite)
class TestDimensionFromDescriptor(TestDescriptor):
    produced_type = Dimension

    def subject(self, descriptor):
        return Dimension.from_descriptor(descriptor)

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_result("A")

    @args({"descriptor": Unit3.C})
    def test_with_aliased_measurement_unit(self):
        self.assert_result("C")

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_result("A")

    def test_returns_same_object_dimension(self):
        descriptor = dimension_1()
        self.assertIs(descriptor, Dimension.from_descriptor(descriptor))

    @args({"descriptor": dimension_3()})
    def test_with_aliased_dimension(self):
        self.assert_result("C")

    def test_returns_same_object_aliased_dimension(self):
        descriptor = dimension_3()
        self.assertIs(descriptor, Dimension.from_descriptor(descriptor))

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)


@add_to(Dimension_test_suite)
class TestDimensionSi(TestDescriptor):
    produced_type = Dimension

    def subject(self, dimension) -> Any:
        return dimension.si()

    @args({"dimension": dimension_1(3)})
    def test_with_exponentiated_dimension(self):
        self.assert_result("(a^3)")

    @args({"dimension": dimension_1()})
    def test_with_simple_dimension(self):
        self.assert_result("a")

    @args({"dimension": Dimension(Unit1.a, 2)})
    def test_with_exponentiated_si_dimension(self):
        self.assert_result("(a^2)")

    @args({"dimension": Dimension(Unit1.a)})
    def test_with_si_dimension(self):
        self.assert_result("a")


@add_to(Dimension_test_suite)
class TestDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return dimension_1().isinstance(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": Unit2})
    def test_with_wrong_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_1(2)})
    def test_with_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestAliasDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return dimension_5().isinstance(generic)

    @args({"generic": generic_dimension_5()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": Unit5})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_aliased_composite_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_4(4)]
            )
        }
    )
    def test_with_wrong_aliased_composite_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestExponentiatedAliasDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return dimension_5(2).isinstance(generic)

    @args({"generic": generic_dimension_5(2)})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": Unit5})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_4(4)]
            )
        }
    )
    def test_with_aliased_composite_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_wrong_aliased_composite_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestAliasedDimensionIsInstance(TestDescriptor):
    def subject(self, generic) -> Any:
        return dimension_1(2).isinstance(generic)

    @args({"generic": generic_dimension_1(2)})
    def test_with_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_6()})
    def test_with_alias_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit6})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestExponentiatedAliasedDimensionIsInstance(TestDescriptor):
    def subject(self, generic) -> Any:
        return dimension_1(4).isinstance(generic)

    @args({"generic": generic_dimension_1(4)})
    def test_with_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_6(2)})
    def test_with_alias_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic):
        return dimension_1().isinstance_equivalent(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_1(2)})
    def test_with_same_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": GenericCompositeDimension([generic_dimension_1()])})
    def test_with_numerator_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_2()]
            )
        }
    )
    def test_with_generic_composite_dimension_same_numerator(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestExponentiatedDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic):
        return dimension_1(3).isinstance_equivalent(generic)

    @args({"generic": generic_dimension_1(3)})
    def test_with_same_generic(self):
        return self.assertResultTrue()

    @args({"generic": Unit3})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3()})
    def test_with_alias_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3(2)})
    def test_with_exponentiated_alias_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestAliasDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic, power=1):
        return dimension_3(power).isinstance_equivalent(generic)

    @args({"generic": generic_dimension_1(3)})
    def test_with_aliased_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_6(3), "power": 2})
    def test_with_other_alias_generic_dimension(self):
        self.assertResultTrue()


@add_to(Dimension_test_suite)
class TestComplexAliasDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic, power=1):
        return dimension_5(power).isinstance_equivalent(generic)

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_aliased_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_4(4)]
            ),
            "power": 2,
        }
    )
    def test_with_exponentiated_aliased_composite_dimension(self):
        self.assertResultTrue()


@add_to(Dimension_test_suite)
class TestDimensionToGeneric(TestDescriptor):
    def test_dimension_to_generic(self):
        self.assertEqual(dimension_1().to_generic(), generic_dimension_1())

    def test_exponentiated_dimension_to_generic(self):
        self.assertEqual(dimension_1(2.5).to_generic(), generic_dimension_1(2.5))


@add_to(Dimension_test_suite)
class TestDimensionInverse(TestDescriptor):
    def test_inverse(self):
        self.assertSequenceEqual(str((Unit1.A**2).inverse()), " / (A^2)")

    def test_object_is_not_persisted(self):
        dimension = dimension_1(2)
        composite = dimension.inverse()
        self.assertIsNot(composite.denominator[0], dimension)


@add_to(Dimension_test_suite)
class TestDimensionMultiplication(TestMeasurementUnitMultiplication):
    """
    Repeat all tests in `TestMeasurementUnitMultiplication` but with dimension_1() as
    descriptor.
    """

    @classmethod
    def build_descriptor(cls):
        return dimension_1()


@add_to(Dimension_test_suite)
class TestDimensionDivision(TestMeasurementUnitDivision):
    """
    Repeat all tests in `TestMeasurementUnitDivision` but with dimension_1() as
    descriptor.
    """

    @classmethod
    def build_descriptor(cls):
        return dimension_1()


@add_to(Dimension_test_suite)
class TestDimensionExponentiation(TestMeasurementUnitExponentiation):
    """
    Repeat all tests in `TestMeasurementUnitExponentiation` but with dimension_1() as
    descriptor.
    """

    def subject(self, value):
        return dimension_1() ** value


@add_to(Dimension_test_suite)
class TestExponentiatedDimensionExponentiation(TestDescriptor):
    produced_type = Dimension

    def subject(self, value):
        return dimension_1(2) ** value

    @args({"value": 12})
    def test_with_int(self):
        self.assert_result("(A^24)")

    @args({"value": -5})
    def test_with_negative_int(self):
        self.assert_result("(A^-10)")

    @args({"value": 0})
    def test_with_zero(self):
        self.assert_result("(A^0)")

    @args({"value": 1.3})
    def test_with_float(self):
        self.assert_result("(A^2.6)")

    @args({"value": None})
    def test_with_none(self):
        self.assertResultRaises(DescriptorExponentError)


@add_to(Dimension_test_suite)
class TestDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return dimension_1() == dimension

    @args({"dimension": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"dimension": dimension_1()})
    def test_with_same_dimension(self):
        self.assertResultTrue()

    @args({"dimension": dimension_1(3)})
    def test_with_same_exponentiated_dimension(self):
        self.assertResultFalse()

    @args({"dimension": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"dimension": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"dimension": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(Dimension_test_suite)
class TestExponentiatedDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return dimension_1(2) == dimension

    @args({"dimension": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"dimension": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionToSi(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, generic):
        return generic.to_si()

    @args({"generic": generic_composite_dimension()})
    def test_with_simple_generic_composite_dimension(self):
        self.assert_result("(a^2) * b / (c^3)")

    @args({"generic": GenericCompositeDimension([generic_dimension_1()])})
    def test_with_numerator_only(self):
        self.assert_result("a")

    @args({"generic": GenericCompositeDimension([], [generic_dimension_2()])})
    def test_with_denominator_only(self):
        self.assert_result(" / b")


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionSimplify(TestDescriptor):
    produced_type = GenericCompositeDimension

    def subject(self, generic):
        generic.simplify()
        return generic

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_2(2)]
            )
        }
    )
    def test_already_simple_composite(self):
        self.assert_result("(Unit1^2) / (Unit2^2)")

    @args({"generic": GenericCompositeDimension([generic_dimension_1()])})
    def test_numerator_composite(self):
        self.assert_result("Unit1")

    @args({"generic": GenericCompositeDimension([], [generic_dimension_1()])})
    def test_denominator_composite(self):
        self.assert_result(" / Unit1")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(-1.2)], [generic_dimension_2(-0.2)]
            )
        }
    )
    def test_negative_exponents(self):
        self.assert_result("(Unit2^0.2) / (Unit1^1.2)")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_1()]
            )
        }
    )
    def test_same_numerator_denominator(self):
        self.assert_result("")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(), generic_dimension_1(2)], [generic_dimension_2()]
            )
        }
    )
    def test_same_numerator_dimensions(self):
        self.assert_result("(Unit1^3) / Unit2")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_2()],
                [generic_dimension_1(1.5), generic_dimension_1()],
            )
        }
    )
    def test_same_denominator_dimensions(self):
        self.assert_result("Unit2 / (Unit1^2.5)")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2), generic_dimension_1(-2)],
                [generic_dimension_2()],
            )
        }
    )
    def test_same_dimensions_zero_sum(self):
        self.assert_result(" / Unit2")


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionSimplified(TestGenericCompositeDimensionSimplify):
    """
    Run all tests in TestGenericCompositeDimensionSimplify but with a different subject.
    """

    def subject(self, generic):
        return generic.simplified()

    def assert_result(self, result_str):
        self.assertResultIsNot(self._subjectKwargs["generic"])
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionAnalyse(TestDescriptor):
    produced_type = GenericCompositeDimension

    def subject(self, generic):
        generic.analyse()
        return generic

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_2()]
            )
        }
    )
    def test_already_analysed_composite(self):
        self.assert_result("Unit1 / Unit2")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_2()]
            )
        }
    )
    def test_with_simple_alias_generic_dimension(self):
        self.assert_result("Unit1 / (Unit4^2) / Unit2")

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_3()]
            )
        }
    )
    def test_with_multiple_alias_generic_dimensions(self):
        self.assert_result("Unit1 / (Unit1^3) / (Unit4^2)")


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionAnalysed(TestGenericCompositeDimensionAnalyse):
    """
    Run all tests in TestGenericCompositeDimensionAnalyse but with a different subject.
    """

    def subject(self, generic):
        return generic.analysed()

    def assert_result(self, result_str):
        self.assertResultIsNot(self._subjectKwargs["generic"])
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionInverseGeneric(TestDescriptor):
    def test_inverse_generic(self):
        self.assertSequenceEqual(
            str(generic_composite_dimension().inverse_generic()),
            "(Unit3^3) / (Unit1^2) / Unit2",
        )

    def test_objects_are_not_persisted(self):
        composite = generic_composite_dimension()
        inverse = composite.inverse_generic()
        self.assertNotEqual(ids(composite.numerator), ids(inverse.denominator))
        self.assertNotEqual(ids(composite.denominator), ids(inverse.numerator))


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        """
        (Unit1^2) / Unit2 / Unit3
        """
        return GenericCompositeDimension(
            [generic_dimension_1(2)], [generic_dimension_2(), generic_dimension_3()]
        )

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("(Unit1^2) * Unit2 / Unit2 / Unit3")

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_result("(Unit1^2) * Unit1 / Unit2 / Unit3")

    @args({"descriptor": generic_dimension_1(3)})
    def test_with_exponentiated_generic_dimension(self):
        self.assert_result("(Unit1^2) * (Unit1^3) / Unit2 / Unit3")

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result("(Unit1^2) * (Unit1^2) * Unit2 / (Unit3^3) / Unit2 / Unit3")

    @args({"descriptor": 78})
    def test_with_int(self):
        self.assert_invalid()


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        """
        (Unit1^2) / Unit2 / Unit3
        """
        return GenericCompositeDimension(
            [generic_dimension_1(2)], [generic_dimension_2(), generic_dimension_3()]
        )

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assert_invalid()

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assert_invalid()

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_invalid()

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assert_result("(Unit1^2) / Unit2 / Unit2 / Unit3")

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_result("(Unit1^2) / Unit1 / Unit2 / Unit3")

    @args({"descriptor": generic_dimension_1(3)})
    def test_with_exponentiated_generic_dimension(self):
        self.assert_result("(Unit1^2) / (Unit1^3) / Unit2 / Unit3")

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_result("(Unit1^2) * (Unit3^3) / (Unit1^2) / Unit2 / Unit2 / Unit3")

    @args({"descriptor": 78})
    def test_with_int(self):
        self.assert_invalid()


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionExponentiation(TestDescriptor):
    produced_type = GenericCompositeDimension

    def subject(self, value):
        return generic_composite_dimension() ** value

    @args({"value": "123"})
    def test_with_invalid_value(self):
        self.assertResultRaises(DescriptorExponentError)

    @args({"value": 1})
    def test_with_one(self):
        self.assert_result("(Unit1^2) * Unit2 / (Unit3^3)")

    @args({"value": -1})
    def test_with_minus_one(self):
        self.assert_result("(Unit1^-2) * (Unit2^-1) / (Unit3^-3)")

    @args({"value": 0.5})
    def test_with_float(self):
        self.assert_result("(Unit2^0.5) * Unit1 / (Unit3^1.5)")


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionEquality(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor() == generic

    @classmethod
    def build_descriptor(cls):
        """
        (Unit1^2) / Unit2
        """
        return GenericCompositeDimension(
            [generic_dimension_1(2)], [generic_dimension_2()]
        )

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1(2)})
    def test_with_numerator_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_2()})
    def test_with_denominator_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_2()], [generic_dimension_1(2)]
            )
        }
    )  # Unit2 / (Unit1^2)
    def test_with_same_inverse_composite_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(2)], [generic_dimension_2()]
            )
        }
    )  # (Unit1^2) / Unit2
    def test_with_same_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_2()]
            )
        }
    )  # Unit1 / Unit2
    def test_with_almost_same_generic_composite_dimensions(self):
        self.assertResultFalse()


@add_to(GenericCompositeDimension_test_suite)
class TestSimpleGenericCompositeDimensionEquality(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor() == generic

    @classmethod
    def build_descriptor(cls):
        """
        (Unit1^2)
        """
        return GenericCompositeDimension([generic_dimension_1(2)], [])

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1(2)})
    def test_with_numerator(self):
        self.assertResultFalse()

    @args({"generic": Unit6})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_6()})
    def test_with_alias_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": GenericCompositeDimension([generic_dimension_1(2)], [])})
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()


@add_to(GenericCompositeDimension_test_suite)
class TestNumeratorGenericCompositeDimensionEquality(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor() == generic

    def build_descriptor(self):
        """
        Unit1 * Unit2
        """
        return GenericCompositeDimension([generic_dimension_1(), generic_dimension_2()])

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_2(), generic_dimension_1()]
            )
        }
    )
    def test_commutative_property(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1(), generic_dimension_1(), generic_dimension_2()]
            )
        }
    )
    def test_multiple_same_dimensions(self):
        self.assertResultFalse()


@add_to(GenericCompositeDimension_test_suite)
class TestDenominatorGenericCompositeDimensionEquality(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor() == generic

    def build_descriptor(self):
        """
        Unit1 / Unit2 / Unit2
        """
        return GenericCompositeDimension(
            [generic_dimension_1()], [generic_dimension_2(), generic_dimension_2()]
        )

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_2()]
            )
        }
    )
    def test_denominator_dimension(self):
        self.assertResultFalse()


@add_to(GenericCompositeDimension_test_suite)
class TestAliasedGenericCompositeDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().is_equivalent(generic)

    def build_descriptor(self):
        return GenericCompositeDimension(
            [generic_dimension_1()], [generic_dimension_4(2)]
        )

    @args({"generic": Unit5})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5()})
    def test_with_alias_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5(2)})
    def test_with_other_generic_dimension(self):
        self.assertResultFalse()


@add_to(GenericCompositeDimension_test_suite)
class TestSingleNumeratorGenericCompositeDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().is_equivalent(generic)

    def build_descriptor(self):
        return GenericCompositeDimension([generic_dimension_3()])

    @args({"generic": Unit3})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()


@add_to(GenericCompositeDimension_test_suite)
class TestComplexAliasGenericCompositeDimensionIsEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().is_equivalent(generic)

    def build_descriptor(self):
        """
        Unit7 / Unit6
        """
        return GenericCompositeDimension(
            [generic_dimension_7()], [generic_dimension_6()]
        )

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_6(), generic_dimension_2()]
            )
        }
    )  # Unit5 / Unit6 / Unit2
    def test_with_other_alias_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()],
                [generic_dimension_4(2), generic_dimension_2(), generic_dimension_6()],
            )
        }
    )  # Unit1/ Unit4^2 / Unit2 / Unit6
    def test_with_aliased_numerator_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_7()], [generic_dimension_1(2)]
            )
        }
    )  # Unit7 / Unit1^2
    def test_with_aliased_denominator_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [],
                [generic_dimension_4(2), generic_dimension_2(), generic_dimension_1()],
            )
        }
    )  # 1 / Unit4^2 / Unit2 / Unit1
    def test_with_fully_aliased_composite_dimension(self):
        self.assertResultTrue()


@add_to(GenericCompositeDimension_test_suite)
class TestGenericCompositeDimensionHasNoUnits(TestDescriptor):
    def test_with_measurement_units(self):
        self.assertFalse(generic_composite_dimension().has_no_units())

    def test_with_no_measurement_units(self):
        self.assertTrue(GenericCompositeDimension().has_no_units())


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionFromDescriptor(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, descriptor):
        return CompositeDimension.from_descriptor(descriptor)

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * B / (C^3)")

    def test_returns_same_object(self):
        descriptor = composite_dimension()
        self.assertIs(descriptor, CompositeDimension.from_descriptor(descriptor))

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(UnitDescriptorTypeError)


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionSi(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, composite):
        return composite.si()

    @args({"composite": CompositeDimension([dimension_1()], [dimension_2()])})
    def test_with_simple_composite(self):
        self.assert_result("a / b")

    @args({"composite": CompositeDimension([dimension_3(2)], [dimension_2(3)])})
    def test_with_composite(self):
        self.assert_result("(c^2) / (b^3)")

    @args({"composite": CompositeDimension([Dimension(Unit1.a)], [Dimension(Unit2.b)])})
    def test_with_si_composite(self):
        self.assert_result("a / b")

    @args({"composite": CompositeDimension([Dimension(Unit1.a)], [dimension_2()])})
    def test_with_partial_si_composite(self):
        self.assert_result("a / b")


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return composite_dimension().isinstance(generic)

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()


@add_to(CompositeDimension_test_suite)
class TestSimpleCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance(generic)

    def build_descriptor(self):
        """
        A
        """
        return CompositeDimension([dimension_1()], [])

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"generic": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestAliasedCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_1()], [dimension_4(2)])

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()], [generic_dimension_4(2)]
            )
        }
    )
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5()})
    def test_with_alias_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestTwiceAliasedCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_5()], [dimension_2()])

    @args({"generic": Unit7})
    def test_with_alias_unit(self):
        self.assertResultFalse()

    @args({"generic": generic_dimension_7()})
    def test_with_alias_dimension(self):
        self.assertResultFalse()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_2()]
            )
        }
    )
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5()})
    def test_with_other_generic_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestNumeratorAliasCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_5()], [dimension_2(2)])

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_2(2)]
            )
        }
    )
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()],
                [generic_dimension_2(2), generic_dimension_4(2)],
            )
        }
    )
    def test_with_aliased_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestDenominatorAliasCompositeDimensionIsInstance(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_2()], [dimension_5()])

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_2()], [generic_dimension_5()]
            )
        }
    )
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_2(), generic_dimension_4(2)],
                [generic_dimension_1()],
            )
        }
    )
    def test_with_aliased_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestAliasedCompositeDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance_equivalent(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_1()], [dimension_4(2)])

    @args({"generic": Unit5})
    def test_with_alias_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5()})
    def test_with_alias_generic_dimension(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_5(2)})
    def test_with_other_generic_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestSingleNumeratorCompositeDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance_equivalent(generic)

    def build_descriptor(self):
        return CompositeDimension([dimension_3()])

    @args({"generic": Unit3})
    def test_with_measurement_unit_type(self):
        self.assertResultTrue()

    @args({"generic": generic_dimension_3()})
    def test_with_generic_dimension(self):
        self.assertResultTrue()


@add_to(CompositeDimension_test_suite)
class TestComplexAliasCompositeDimensionIsInstanceEquivalent(TestDescriptor):
    def subject(self, generic):
        return self.build_descriptor().isinstance_equivalent(generic)

    def build_descriptor(self):
        """
        G / F
        """
        return CompositeDimension([dimension_7()], [dimension_6()])

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_5()], [generic_dimension_6(), generic_dimension_2()]
            )
        }
    )  # Unit5 / Unit6 / Unit2
    def test_with_other_alias_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_1()],
                [generic_dimension_4(2), generic_dimension_2(), generic_dimension_6()],
            )
        }
    )  # Unit1/ Unit4^2 / Unit2 / Unit6
    def test_with_aliased_numerator_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [generic_dimension_7()], [generic_dimension_1(2)]
            )
        }
    )  # Unit7 / Unit1^2
    def test_with_aliased_denominator_composite_dimension(self):
        self.assertResultTrue()

    @args(
        {
            "generic": GenericCompositeDimension(
                [],
                [generic_dimension_4(2), generic_dimension_2(), generic_dimension_1()],
            )
        }
    )  # 1 / Unit4^2 / Unit2 / Unit1
    def test_with_fully_aliased_composite_dimension(self):
        self.assertResultTrue()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionToGeneric(TestDescriptor):
    def test_to_generic(self):
        self.assertEqual(
            composite_dimension().to_generic(), generic_composite_dimension()
        )


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionGetNumerator(TestDescriptor):
    def subject(self, generic):
        return composite_dimension().get_numerator(generic)

    def default(self):
        return None

    def assert_default(self):
        self.assertResult(self.default())

    @args({"generic": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_default()

    @args({"generic": dimension_1()})
    def test_with_dimension(self):
        self.assert_default()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_default()

    @args({"generic": Unit2})
    def test_with_numerator_measurement_unit_type(self):
        self.assertResult(dimension_2())

    @args({"generic": Unit1})
    def test_with_almost_numerator_measurement_unit_type(self):
        self.assert_default()

    @args({"generic": Unit3})
    def test_with_denominator_measurement_unit_type(self):
        self.assert_default()

    @args({"generic": generic_dimension_1(2)})
    def test_with_numerator_exponentiated_generic_dimension(self):
        self.assertResult(dimension_1(2))

    @args({"generic": generic_dimension_2()})
    def test_with_numerator_generic_dimension(self):
        self.assertResult(dimension_2())

    @args({"generic": dimension_3()})
    def test_with_denominator_generic_dimension(self):
        self.assert_default()

    @args({"generic": dimension_3(3)})
    def test_with_denominator_exponentiated_generic_dimension(self):
        self.assert_default()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_default()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionGetNumeratorDefault(TestCompositeDimensionGetNumerator):
    """
    Run all tests in `TestCompositeDimensionGetNumerator` but pass a default value to
    the `get_numerator` function;
    """

    def subject(self, generic):
        return composite_dimension().get_numerator(generic, self.default())

    def default(self):
        return "default value"

    def assert_default(self):
        self.assertResult(self.default())


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionGetDenominator(TestDescriptor):
    def subject(self, generic):
        return composite_dimension().get_denominator(generic)

    def default(self):
        return None

    def assert_default(self):
        self.assertResult(self.default())

    @args({"generic": Unit3.C})
    def test_with_measurement_unit(self):
        self.assert_default()

    @args({"generic": dimension_3()})
    def test_with_dimension(self):
        self.assert_default()

    @args({"generic": dimension_3(3)})
    def test_with_exponentiated_dimension(self):
        self.assert_default()

    @args({"generic": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_default()

    @args({"generic": Unit3})
    def test_with_denominator_measurement_unit_type(self):
        self.assert_default()

    @args({"generic": Unit2})
    def test_with_numerator_measurement_unit_type(self):
        self.assert_default()

    @args({"generic": generic_dimension_3(3)})
    def test_with_denominator_exponentiated_generic_dimension(self):
        self.assertResult(dimension_3(3))

    @args({"generic": dimension_2()})
    def test_with_numerator_generic_dimension(self):
        self.assert_default()

    @args({"generic": dimension_1(2)})
    def test_with_numerator_exponentiated_generic_dimension(self):
        self.assert_default()

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_default()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionGetDenominatorDefault(TestCompositeDimensionGetDenominator):
    """
    Run all tests in `TestCompositeDimensionGetDenominator` but pass a default value to
    the `get_denominator` function;
    """

    def subject(self, generic):
        return composite_dimension().get_denominator(generic, self.default())

    def default(self):
        return "default value"

    def assert_default(self):
        self.assertResult(self.default())


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionSimplify(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, composite):
        composite.simplify()
        return composite

    @args({"composite": CompositeDimension([dimension_1(2)], [dimension_2(2)])})
    def test_already_simple_composite(self):
        self.assert_result("(A^2) / (B^2)")

    @args({"composite": CompositeDimension([dimension_1()], [])})
    def test_numerator_composite(self):
        self.assert_result("A")

    @args({"composite": CompositeDimension([], [dimension_1()])})
    def test_denominator_composite(self):
        self.assert_result(" / A")

    @args({"composite": CompositeDimension([dimension_1(-1.6)], [dimension_3(-2)])})
    def test_negative_exponents(self):
        self.assert_result("(C^2) / (A^1.6)")

    @args({"composite": CompositeDimension([dimension_1()], [dimension_1()])})
    def test_same_numerator_denominator(self):
        self.assert_result("")

    @args(
        {
            "composite": CompositeDimension(
                [dimension_1(), dimension_1(2)], [dimension_2()]
            )
        }
    )
    def test_same_numerator_dimensions(self):
        self.assert_result("(A^3) / B")

    @args(
        {
            "composite": CompositeDimension(
                [dimension_2()], [dimension_3(2), dimension_3(3.2)]
            )
        }
    )
    def test_same_denominator_dimensions(self):
        self.assert_result("B / (C^5.2)")

    @args(
        {
            "composite": CompositeDimension(
                [dimension_1(2), dimension_1(-2)], [dimension_3()]
            )
        }
    )
    def test_same_numerator_dimensions_zero_sum(self):
        self.assert_result(" / C")


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionSimplified(TestCompositeDimensionSimplify):
    """
    Run all tests in TestCompositeDimensionSimplify but with a different subject.
    """

    def subject(self, composite):
        return composite.simplified()

    def assert_result(self, result_str):
        self.assertResultIsNot(self._subjectKwargs["composite"])
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionInverse(TestDescriptor):
    def test_inverse_generic(self):
        self.assertSequenceEqual(
            str(composite_dimension().inverse()),
            "(C^3) / (A^2) / B",
        )

    def test_objects_are_not_persisted(self):
        composite = composite_dimension()
        inverse = composite.inverse()
        self.assertNotEqual(ids(composite.numerator), ids(inverse.denominator))
        self.assertNotEqual(ids(composite.denominator), ids(inverse.numerator))


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionHasNoUnits(TestDescriptor):
    def test_with_units(self):
        self.assertFalse(composite_dimension().has_no_units())

    def test_with_no_units(self):
        self.assertTrue(CompositeDimension().has_no_units())

    def test_with_same_unit_type(self):
        self.assertFalse(CompositeDimension([Unit1.A], [Unit1.a]).has_no_units())

    def test_with_same_unit(self):
        self.assertFalse(CompositeDimension([Unit1.A], [Unit1.A]).has_no_units())


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = CompositeDimension

    def build_descriptor(self):
        return composite_dimension()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_result("(A^2) * A * B / (C^3)")

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_result("(A^2) * A * B / (C^3)")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * (A^2) * B * B / (C^3) / (C^3)")

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = CompositeDimension

    def build_descriptor(self):
        return composite_dimension()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assert_result("(A^2) * B / (C^3) / A")

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assert_result("(A^2) * B / (C^3) / A")

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * (C^3) * B / (A^2) / (C^3) / B")

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assert_invalid()

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assert_invalid()

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assert_invalid()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionExponentiation(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, value):
        return composite_dimension() ** value

    @args({"value": "123"})
    def test_with_invalid_value(self):
        self.assertResultRaises(DescriptorExponentError)

    @args({"value": 1})
    def test_with_one(self):
        self.assert_result("(A^2) * B / (C^3)")

    @args({"value": -1})
    def test_with_minus_one(self):
        self.assert_result("(A^-2) * (B^-1) / (C^-3)")

    @args({"value": 0.5})
    def test_with_float(self):
        self.assert_result("(B^0.5) * A / (C^1.5)")


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return self.build_descriptor() == dimension

    def build_descriptor(self):
        """
        (A^2) / B
        """
        return CompositeDimension([dimension_1(2)], [dimension_2()])

    @args({"dimension": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultFalse()

    @args({"dimension": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"dimension": dimension_1(2)})
    def test_with_numerator(self):
        self.assertResultFalse()

    @args({"dimension": dimension_2()})
    def test_with_denominator(self):
        self.assertResultFalse()

    @args({"dimension": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultFalse()

    @args({"dimension": CompositeDimension([dimension_1(2)], [dimension_2()])})
    def test_with_same_composite_dimension(self):
        self.assertResultTrue()

    @args({"dimension": CompositeDimension([dimension_2()], [dimension_1(2)])})
    def test_with_inverse_composite_dimension(self):
        self.assertResultFalse()

    @args({"dimension": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultFalse()

    @args({"dimension": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultFalse()

    @args({"dimension": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestSimpleCompositeDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return self.build_descriptor() == dimension

    @classmethod
    def build_descriptor(cls):
        """
        (A^2)
        """
        return CompositeDimension([dimension_1(2)], [])

    @args({"dimension": dimension_1()})
    def test_with_dimension(self):
        self.assertResultFalse()

    @args({"dimension": dimension_1(2)})
    def test_with_exponentiated_dimension(self):
        self.assertResultFalse()

    @args({"dimension": CompositeDimension([dimension_1(2)], [])})
    def test_with_composite_dimension(self):
        self.assertResultTrue()


@add_to(CompositeDimension_test_suite)
class TestNumeratorCompositeDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return self.build_descriptor() == dimension

    def build_descriptor(self):
        """
        A * B
        """
        return Unit1.A * Unit2.B

    @args({"dimension": CompositeDimension([dimension_2(), dimension_1()])})
    def test_commutative_property(self):
        self.assertResultTrue()

    @args(
        {"dimension": CompositeDimension([dimension_1(), dimension_1(), dimension_2()])}
    )
    def test_multiple_same_dimensions(self):
        self.assertResultFalse()


@add_to(CompositeDimension_test_suite)
class TestDenominatorCompositeDimensionEquality(TestDescriptor):
    def subject(self, dimension):
        return self.build_descriptor() == dimension

    def build_descriptor(self):
        """
        A / B / B
        """
        return CompositeDimension([dimension_1()], [dimension_2(), dimension_2()])

    @args({"dimension": CompositeDimension([dimension_1()], [dimension_2()])})
    def test_denominator_dimension(self):
        self.assertResultFalse()


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(descriptors_test_suite)
