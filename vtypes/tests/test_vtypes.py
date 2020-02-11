#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.
import sys

import pytest
from six import with_metaclass
from valid8 import ValidationError

from vtypes.core import VType, VTypeMeta
from vtypes import vtype


@pytest.mark.parametrize('val_to_test,valid_type, valid_value',
                         [(1, True, True),
                          (-1, True, False),
                          ('1', False, True if sys.version_info < (3, 0) else False)  # in python 2 '1' > 0 returns True
                          ])
@pytest.mark.parametrize("validator_style", ['callable', 'tuple', 'dict', 'list'],
                         ids="validator_style={}".format)
@pytest.mark.parametrize("vtype_style", ['function', 'class_unofficial'],
                         ids="vtype_style={}".format)
def test_vtype_basic(validator_style, vtype_style, val_to_test, valid_type, valid_value):

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

    # values test
    if valid_type and valid_value:
        assert isinstance(val_to_test, PositiveInt)
        PositiveInt.assert_valid('s', val_to_test)
    else:
        assert not isinstance(val_to_test, PositiveInt)
        with pytest.raises(ValidationError):
            PositiveInt.assert_valid('s', val_to_test)
    assert PositiveInt.has_valid_type(val_to_test) is valid_type
    assert PositiveInt.has_valid_value(val_to_test) is valid_value
    assert PositiveInt.has_valid_value(val_to_test, inherited_validators=False) is valid_value

    # intuitive subclass behaviour
    assert issubclass(VType, VType)
    assert not issubclass(int, VType)
    assert issubclass(PositiveInt, VType)
    assert not issubclass(VType, PositiveInt)
    assert issubclass(PositiveInt, int)
    assert not issubclass(int, PositiveInt)

    for cls in (PositiveInt, ):
        assert '__type__' in cls.__dict__
        assert '__validators__' in cls.__dict__
        assert '_validator' in cls.__dict__

    # make sure the string representation will be correct
    assert PositiveInt.__module__ == test_vtype_basic.__module__


@pytest.mark.parametrize('val_to_test,valid_type, valid_value',
                         [('1', True, True),
                          ('', True, False),
                          (1, False, False)])
def test_vtypes_inheritance(val_to_test, valid_type, valid_value):
    """ Test with inherited vtypes """

    with pytest.raises(TypeError):
        class NonEmpty(with_metaclass(VTypeMeta, object)):
            __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmpty(VType):
        __validators__ = {'should be non empty': lambda x: len(x) > 0}

    class NonEmptyStr(NonEmpty, str):
        pass

    # values test
    if valid_type and valid_value:
        assert isinstance(val_to_test, NonEmptyStr)
        NonEmptyStr.assert_valid('s', val_to_test)
    else:
        assert not isinstance(val_to_test, NonEmptyStr)
        with pytest.raises(ValidationError):
            NonEmptyStr.assert_valid('s', val_to_test)
    assert NonEmptyStr.has_valid_type(val_to_test) is valid_type
    assert NonEmptyStr.has_valid_value(val_to_test) is valid_value
    # this one is always True since we do not look at inherited
    assert NonEmptyStr.has_valid_value(val_to_test, inherited_validators=False) is True

    # intuitive subclass behaviour
    assert issubclass(NonEmptyStr, NonEmpty)
    assert not issubclass(NonEmpty, NonEmptyStr)
    assert issubclass(NonEmptyStr, str)
    assert not issubclass(str, NonEmptyStr)
    assert issubclass(NonEmptyStr, VType)
    assert not issubclass(VType, NonEmptyStr)

    for cls in (NonEmpty, NonEmptyStr):
        assert '__type__' in cls.__dict__
        assert '__validators__' in cls.__dict__
        assert '_validator' in cls.__dict__