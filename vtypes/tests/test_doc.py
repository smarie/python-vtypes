#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.
import pytest
from valid8 import ValidationError

from vtypes import vtype


def test_doc_first():
    """The first example in the doc"""

    PositiveInt = vtype('PositiveInt', int, {'should be positive': lambda x: x >= 0})

    assert isinstance(1, PositiveInt)
    assert not isinstance(-1, PositiveInt)

    with pytest.raises(ValidationError):
        PositiveInt.validate('x', -1)

    assert PositiveInt.has_valid_type(-1)
    assert not PositiveInt.has_valid_value(-1)


def test_doc_second():
    from vtypes import VType

    class NonEmpty(VType):
        """A VType describing non-empty containers, with strictly positive length."""
        __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmptyStr(NonEmpty, str):
        """A VType for non-empty strings"""

    class AlternateNonEmptyStr(VType):
        """A VType for non-empty strings - alternate style"""
        __type__ = NonEmpty, str

    assert isinstance('hoho', NonEmpty)
    assert not isinstance('', NonEmpty)
    assert not isinstance([], NonEmpty)
    assert isinstance([1], NonEmpty)
    assert not isinstance(1, NonEmpty)
    assert isinstance('hoho', NonEmptyStr)
    assert isinstance('hoho', AlternateNonEmptyStr)
    assert not isinstance('', NonEmptyStr)
    assert not isinstance('', AlternateNonEmptyStr)
    assert not isinstance(1, NonEmptyStr)
    assert not isinstance(1, AlternateNonEmptyStr)
