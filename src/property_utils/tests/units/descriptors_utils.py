from typing import Callable, Type
from abc import abstractmethod

from unittest_extensions import TestCase

from property_utils.units.descriptors import Descriptor
from property_utils.exceptions.units.descriptors import DescriptorBinaryOperationError


class TestDescriptor(TestCase):
    """
    Base class for descriptor test cases.
    """

    produced_type: Type[Descriptor]

    def assert_result(self, result_str):
        self.assertResultIsInstance(self.produced_type)
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)

    def assert_invalid(self, expected_regex=None):
        if expected_regex is None:
            self.assertResultRaises(DescriptorBinaryOperationError)
        else:
            self.assertResultRaisesRegex(DescriptorBinaryOperationError, expected_regex)


class TestDescriptorBinaryOperation(TestDescriptor):
    """
    Defines helper methods for descriptor binary operation test cases.
    """

    operator: Callable

    def subject(self, descriptor):
        return self.operator(self.build_descriptor(), descriptor)

    @classmethod
    @abstractmethod
    def build_descriptor(cls) -> Descriptor: ...
