from operator import gt, add, sub, ge

from unittest_extensions import args, TestCase

from property_utils.units import KELVIN, MOL, JOULE
from property_utils.properties import p
from property_utils.exceptions import PropertyBinaryOperationError


class TestPublicPropertyOperations(TestCase):
    def subject(self, p1, p2, op):
        return op(p1, p2)

    def assert_result(self, result_str):
        self.assertSequenceEqual(str(self.result()), result_str, str)

    @args(
        {
            "p1": p(15, JOULE / MOL / KELVIN),
            "p2": p(20.2, JOULE / MOL / KELVIN),
            "op": gt,
        }
    )
    def test_greater_than(self):
        self.assertResultFalse()

    @args({"p1": p(10), "p2": p(9, MOL), "op": gt})
    def test_greater_than_with_different_units(self):
        self.assertResultRaisesRegex(
            PropertyBinaryOperationError,
            "cannot compare \(9 mol\) to \(10 \); \(9 mol\) must have \(NonDimensionalUnit\) units. ",
        )

    @args({"p1": p(293, KELVIN), "p2": p(10, KELVIN), "op": add})
    def test_add(self):
        self.assert_result("303 K")

    @args({"p1": p(5, MOL), "p2": p(1.02, MOL), "op": sub})
    def test_sub(self):
        self.assert_result("3.98 mol")

    @args({"p1": p(11, JOULE / KELVIN), "p2": p(10, JOULE / KELVIN), "op": ge})
    def test_greater_or_equal(self):
        self.assertResultTrue()
