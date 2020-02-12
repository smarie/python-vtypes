#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.
import sys

import pytest
from six import with_metaclass
from valid8 import ValidationError

from vtypes.core import VTypeMeta
from vtypes import vtype, is_vtype, VType


@pytest.mark.parametrize('val_to_test,valid_type, valid_value',
                         [(1, True, True),
                          (-1, True, False),
                          ('1', False, True if sys.version_info < (3, 0) else False)  # in python 2 '1' > 0 returns True
                          ])
@pytest.mark.parametrize("validator_style", ['callable', 'tuple', 'dict', 'list'],
                         ids="validator_style={}".format)
@pytest.mark.parametrize("vtype_style", ['function', 'class'],
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

    if vtype_style == 'class':
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
        PositiveInt.validate('s', val_to_test)
    else:
        assert not isinstance(val_to_test, PositiveInt)
        with pytest.raises(ValidationError):
            PositiveInt.validate('s', val_to_test)
    assert PositiveInt.has_valid_type(val_to_test) is valid_type
    assert PositiveInt.has_valid_value(val_to_test) is valid_value
    assert PositiveInt.has_valid_value(val_to_test, inherited_validators=False) is valid_value

    # intuitive subclass behaviour
    assert issubclass(VType, VType)
    assert not issubclass(int, VType)
    assert issubclass(PositiveInt, VType)
    assert not issubclass(VType, PositiveInt)

    # This is the precise reason why we need to put the __type__ in the bases
    assert issubclass(PositiveInt, int)

    assert not issubclass(int, PositiveInt)

    for cls in (PositiveInt, ):
        assert '__type__' in cls.__dict__
        assert '__validators__' in cls.__dict__
        assert '_validator' in cls.__dict__

    # make sure the string representation will be correct
    assert PositiveInt.__module__ == test_vtype_basic.__module__

    # is_vtype
    assert not is_vtype(VTypeMeta)
    assert is_vtype(VType)
    assert is_vtype(PositiveInt)
    assert not is_vtype(1)
    assert not is_vtype(int)


def test_vtype_direct_vtype_meta():
    """Tests that one MUST inherit from VType when using the class style """

    with pytest.raises(TypeError):
        # TypeError: It is not possible to create a VType without inheriting from `VType`
        class NotInheritingVType(with_metaclass(VTypeMeta, object)):
            pass


def test_extra_class_attr():
    """Tests that one cannot define other attributes on `VType` classes"""
    with pytest.raises(TypeError):
        # TypeError: It is not possible to create a VType without inheriting from `VType`
        class NotInheritingVType(with_metaclass(VTypeMeta, object)):
            pass


@pytest.mark.parametrize("vtype_style", ['function', 'class', 'class2'],
                         ids="vtype_style={}".format)
@pytest.mark.parametrize('val_to_test,valid_type, valid_value',
                         [('1', True, True),
                          ('', True, False),
                          (1, False, False)])
def test_vtypes_inheritance(vtype_style, val_to_test, valid_type, valid_value):
    """ Test with inherited vtypes """

    validators = {'should be non empty': lambda x: len(x) > 0}

    if vtype_style == 'class':
        class NonEmpty(VType):
            __validators__ = validators

        class NonEmptyStr(NonEmpty, str):
            pass
    elif vtype_style == 'class2':
        class NonEmpty(VType):
            __validators__ = validators

        class NonEmptyStr(VType):
            """A VType for non-empty strings - alternate style"""
            __type__ = NonEmpty, str

    elif vtype_style == 'function':
        NonEmpty = vtype('NonEmpty', (), validators)
        NonEmptyStr = vtype('NonEmptyStr', (NonEmpty, str), ())
    else:
        raise ValueError(vtype_style)

    # values test
    if valid_type and valid_value:
        assert isinstance(val_to_test, NonEmptyStr)
        NonEmptyStr.validate('s', val_to_test)
    else:
        assert not isinstance(val_to_test, NonEmptyStr)
        with pytest.raises(ValidationError):
            NonEmptyStr.validate('s', val_to_test)
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
