#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.

import pytest
from six import with_metaclass
from valid8 import ValidationError

from vtypes.core import VType, VTypeMeta
from vtypes import vtype


@pytest.mark.parametrize("validator_style", ['callable', 'tuple', 'dict', 'list'],
                         ids="validator_style={}".format)
@pytest.mark.parametrize("vtype_style", ['function', 'class_unofficial'],
                         ids="vtype_style={}".format)
def test_vtype_basic(validator_style, vtype_style):

    if validator_style == 'callable':
        validators = lambda x: x >= 0
    elif validator_style == 'tuple':
        validators = (lambda x: x >= 0, 'should be positive')
    elif validator_style == 'dict':
        validators = {'should be positive': lambda x: x >= 0}
    elif validator_style == 'list':
        validators = [(lambda x: x >= 0, 'should be positive')]
    else:
        raise ValueError(validator_style)

    if vtype_style == 'class_unofficial':
        # this style will be abandoned
        class PositiveInt(VType):
            __type__ = int
            __validators__ = validators
    elif vtype_style == 'function':
        PositiveInt = vtype('PositiveInt', int, validators)
    else:
        raise ValueError(vtype_style)

    # internals check
    assert PositiveInt.__type__ == (int, )

    # usage of the vtype for validation
    assert isinstance(1, PositiveInt)
    assert not isinstance(-1, PositiveInt)
    with pytest.raises(ValidationError):
        PositiveInt.assert_valid('x', -1)

    assert not isinstance('1', PositiveInt)
    with pytest.raises(ValidationError):
        PositiveInt.assert_valid('x', '1')

    # intuitive subclass behaviour
    assert issubclass(VType, VType)
    assert not issubclass(int, VType)
    assert issubclass(PositiveInt, VType)
    assert not issubclass(VType, PositiveInt)
    assert issubclass(PositiveInt, int)
    assert not issubclass(int, PositiveInt)

    # make sure the string representation will be correct
    assert PositiveInt.__module__ == test_vtype_basic.__module__


def test_vtypes_inheritance():
    with pytest.raises(TypeError):
        class NonEmpty(with_metaclass(VTypeMeta, object)):
            __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmpty(VType):
        __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmptyStr(NonEmpty, str):
        pass

    assert isinstance('1', NonEmptyStr)
    assert not isinstance('', NonEmptyStr)
    assert not isinstance(1, NonEmptyStr)

    # intuitive subclass behaviour
    assert issubclass(NonEmptyStr, NonEmpty)
    assert not issubclass(NonEmpty, NonEmptyStr)
    assert issubclass(NonEmptyStr, str)
    assert not issubclass(str, NonEmptyStr)
    assert issubclass(NonEmptyStr, VType)
    assert not issubclass(VType, NonEmptyStr)
