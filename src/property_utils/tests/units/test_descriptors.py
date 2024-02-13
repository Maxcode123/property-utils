from unittest import TestSuite, TextTestRunner
from operator import mul, truediv

from unittest_extensions import args

from property_utils.units.descriptors import (
    MeasurementUnit,
    AliasMeasurementUnit,
    Dimension,
    CompositeDimension,
    GenericDimension,
    GenericCompositeDimension,
)
from property_utils.exceptions.exceptions import (
    InvalidDescriptorBinaryOperation,
    InvalidDescriptorExponent,
    WrongUnitDescriptorType,
)
from property_utils.tests.utils import add_to
from property_utils.tests.units.descriptors_utils import (
    TestDescriptor,
    TestDescriptorBinaryOperation,
)


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


class Unit1(MeasurementUnit):
    A = "A"


class Unit2(MeasurementUnit):
    B = "B"


class Unit3(AliasMeasurementUnit):
    C = "C"


def dimension_1(power: float = 1) -> Dimension:
    """
    A^power
    """
    return Dimension(Unit1.A, power)


def dimension_2(power: float = 1) -> Dimension:
    """
    B^power
    """
    return Dimension(Unit2.B, power)


def dimension_3(power: float = 1) -> Dimension:
    """
    C^power
    """
    return Dimension(Unit3.C, power)


def generic_dimension_1(power: float = 1) -> GenericDimension:
    """
    Unit1^power
    """
    return GenericDimension(Unit1, power)


def generic_dimension_2(power: float = 1) -> GenericDimension:
    """
    Unit2^power
    """
    return GenericDimension(Unit2, power)


def generic_dimension_3(power: float = 1) -> GenericDimension:
    """
    Unit3^power
    """
    return GenericDimension(Unit3, power)


def composite_dimension() -> CompositeDimension:
    """
    (A^2) * B / (C^3)
    """
    return CompositeDimension([dimension_1(2), dimension_2()], [dimension_3(3)])


def generic_composite_dimension() -> GenericCompositeDimension:
    """
    (Unit1^2) * Unit2 / (Unit3^3)
    """
    return GenericCompositeDimension(
        [generic_dimension_1(2), generic_dimension_2()], [generic_dimension_3(3)]
    )


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": 100})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": Unit2.B})
    def test_with_measurement_unit(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": 23})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorExponent)


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
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)


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
class TestMeasurementUnitToGeneric(TestDescriptor):
    def test_to_generic(self):
        self.assertEqual(Unit1.A.to_generic(), Unit1)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": 78})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_2()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": 0})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorExponent)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitFromDescriptor(TestDescriptor):
    def subject(self, descriptor):
        return AliasMeasurementUnit.from_descriptor(descriptor)

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": Unit3.C})
    def test_with_aliased_measurement_unit(self):
        self.assertResult(Unit3.C)

    def test_returns_same_object(self):
        descriptor = Unit3.C
        self.assertIs(descriptor, AliasMeasurementUnit.from_descriptor(descriptor))

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": dimension_3()})
    def test_with_aliased_dimension(self):
        self.assertResult(Unit3.C)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)


@add_to(AliasMeasurementUnit_test_suite)
class TestAliasMeasurementUnitIsInstance(TestDescriptor):
    def subject(self, generic):
        return Unit3.C.isinstance(generic)

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

    @args({"generic": Unit3})
    def test_with_aliased_measurement_unit_type(self):
        self.assertResultTrue()

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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": -99})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": 9})
    def test_with_int(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorExponent)


@add_to(GenericDimension_test_suite)
class TestGenericDimensionMultiplication(TestDescriptorBinaryOperation):
    operator = mul
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return generic_dimension_1()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


@add_to(GenericDimension_test_suite)
class TestGenericDimensionDivision(TestDescriptorBinaryOperation):
    operator = truediv
    produced_type = GenericCompositeDimension

    @classmethod
    def build_descriptor(cls):
        return generic_dimension_1()

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorExponent)


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
        self.assertResultRaises(InvalidDescriptorExponent)


@add_to(GenericCompositeDimension_test_suite)
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

    @args({"generic": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultFalse()


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
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": Unit2})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)


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
class TestDimensionToGeneric(TestDescriptor):
    def test_dimension_to_generic(self):
        self.assertEqual(dimension_1().to_generic(), generic_dimension_1())

    def test_exponentiated_dimension_to_generic(self):
        self.assertEqual(dimension_1(2.5).to_generic(), generic_dimension_1(2.5))


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
        self.assertResultRaises(InvalidDescriptorExponent)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": dimension_2()})
    def test_with_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
    def test_with_exponentiated_generic_dimension(self):
        self.assertResultFalse()

    @args({"generic": GenericCompositeDimension([generic_dimension_1(2)], [])})
    def test_with_generic_composite_dimension(self):
        self.assertResultTrue()


@add_to(CompositeDimension_test_suite)
class TestCompositeDimensionFromDescriptor(TestDescriptor):
    produced_type = CompositeDimension

    def subject(self, descriptor):
        return CompositeDimension.from_descriptor(descriptor)

    @args({"descriptor": Unit1.A})
    def test_with_measurement_unit(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": dimension_1()})
    def test_with_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": composite_dimension()})
    def test_with_composite_dimension(self):
        self.assert_result("(A^2) * B / (C^3)")

    def test_returns_same_object(self):
        descriptor = composite_dimension()
        self.assertIs(descriptor, CompositeDimension.from_descriptor(descriptor))

    @args({"descriptor": Unit1})
    def test_with_measurement_unit_type(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(WrongUnitDescriptorType)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_dimension_1()})
    def test_with_generic_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)

    @args({"descriptor": generic_composite_dimension()})
    def test_with_generic_composite_dimension(self):
        self.assertResultRaises(InvalidDescriptorBinaryOperation)


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


if __name__ == "__main__":
    runner = TextTestRunner()
    runner.run(descriptors_test_suite)
