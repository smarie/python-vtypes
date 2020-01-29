#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.

#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
from vtypes import VType


def test_vtype_basic():

    class PositiveInt(VType):
        __types__ = int
        __validators__ = {'should be positive': lambda x: x >= 0}

    assert PositiveInt.__types__ == (int, )
    assert isinstance(1, PositiveInt)
    assert not isinstance(-1, PositiveInt)
    assert not isinstance('1', PositiveInt)


def test_vtypes_advanced():
    class NonEmpty(VType):
        __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmptyStr(NonEmpty, str):
        pass

    assert isinstance('1', NonEmptyStr)
    assert not isinstance('', NonEmptyStr)
    assert not isinstance(1, NonEmptyStr)
