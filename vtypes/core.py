#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.
from abc import ABCMeta

from six import with_metaclass

try:
    from typing import Type, Union, Tuple, Iterable, Mapping, Optional
    from valid8.common_syntax import ValidationFuncs, ValidationFuncDefinition, VFDefinitionElement
except ImportError:
    pass

from valid8 import validate
from valid8.common_syntax import FunctionDefinitionError
from valid8.entry_points import Validator, ValidationError


def _process_validators(validators  # type: ValidationFuncs
                        ):
    # type: (...) -> Optional[Iterable[ValidationFuncDefinition, Mapping[VFDefinitionElement, Union[VFDefinitionElement, Tuple[VFDefinitionElement, ...]]]]]
    """
    Transforms validators into an iterable for sure, or none
    :param validators:
    :return:
    """
    try:  # dict ?
        validators.keys()
    except (AttributeError, FunctionDefinitionError):  # FunctionDefinitionError when mini_lambda
        if isinstance(validators, tuple):
            # single tuple
            if len(validators) == 0:
                return ()
            else:
                validators = (validators,)
        else:
            try:  # iterable
                iter(validators)
            except (TypeError, FunctionDefinitionError):  # FunctionDefinitionError when mini_lambda
                # single
                validators = (validators,)
            else:
                if len(validators) == 0:
                    return ()
    else:
        # dict
        if len(validators) == 0:
            return ()
        validators = (validators,)

    return validators


class VTypeMeta(ABCMeta):
    """
    The metaclass for VTypes. It implements `isinstance` according to the expected behaviour.

    When a class inherits from `VType`, it is manipulated by the `VTypeMeta` metaclass upon creation
    so that its `__types__` and `__validators__` represent the synthesis of all of its ancestors.
    """
    def __new__(mcls, name, bases, attrs):
        try:
            # is mcls the original VType class ?
            VType
        except NameError:
            # yes: shortcut just create it
            return super(VTypeMeta, mcls).__new__(mcls, name, bases, attrs)
        else:
            # no: a derived class. Let's consolidate the types and validators of all the bases
            _types = []
            _validators = []

            for b in bases:
                if b is VType or b is object:
                    continue

                # is this a vtype ?
                try:
                    _isvtype = b.is_vtype()
                except AttributeError:
                    _isvtype = False
                if _isvtype:
                    # yes: combine types and validators
                    _types += b.__types__
                    _validators += b.__validators__
                else:
                    # no: append to types
                    _types.append(b)

            # final __types__
            try:
                # is there a __types__ attribute on the final class ?
                _lasttypes_ = attrs['__types__']
            except KeyError:
                # no - only use the consolidated types (if any)
                pass
            else:
                # yes - (a) auto-convert types to tuple of types if needed and (b) combine with inherited
                if isinstance(_lasttypes_, type):
                    _types.append(_lasttypes_)
                else:
                    _types += _lasttypes_
            if len(_types) > 0:
                attrs['__types__'] = tuple(_types)

            # final __validators__
            try:
                # is there a __validators__ attribute on the final class ?
                _lastvalidators_ = attrs['__validators__']
            except KeyError:
                # no - only use the consolidated validators *if any*
                pass
            else:
                # yes - combine with the inherited if any
                _lastvalidators_ = _process_validators(_lastvalidators_)
                _validators += _lastvalidators_

            if len(_validators) > 0:
                attrs['__validators__'] = tuple(_validators)

            return super(VTypeMeta, mcls).__new__(mcls, name, bases, attrs)

    def __init__(cls,  # type: VType
                 name, bases, attrs):
        super(VTypeMeta, cls).__init__(name, bases, attrs)
        cls.init_validator()

    def __instancecheck__(cls,  # type:  Type[VType]
                          obj):
        return isinstance(obj, cls.__types__) and cls.has_valid_value(obj)

    def __subclasscheck__(cls, subclass):
        raise Exception("Subclass check can not be performed on a VType yet.")


class VTypeValidator(Validator):
    """
    Represents a `Validator` responsible to validate a `vtype`
    """
    __slots__ = '__weakref__', 'vtype'

    def __init__(self,
                 vtype,       # type: VType
                 validators,  # type: ValidationFuncs
                 **kwargs
                 ):
        # store this additional info about the function been validated
        self.vtype = vtype

        super(VTypeValidator, self).__init__(*validators, **kwargs)


class VType(with_metaclass(VTypeMeta, object)):
    """
    The super class of all `VType`s.

    When a class inherits from `VType`, it is manipulated by the `VTypeMeta` metaclass upon creation
    so that its `__types__` and `__validators__` represent the synthesis of all of its ancestors.

    Also at class creation time a `VTypeValidator` instance is created, that will be used in all subsequent checks.
    Therefore if you dynamically update `__validators__`, you should explicitly call `cls.init_validator()` to refresh
    the validator associated with the class.
    """
    __types__ = ()         # type: Union[Type, Tuple[Type]]
    __validators__ = ()    # type: ValidationFuncs
    __error_type__ = None  # type: Type[ValidationError]
    __help_msg__ = None    # type: str

    _validator = None      # type: Validator

    @classmethod
    def is_vtype(cls):
        # type: (...) -> bool
        """
        Used by the metaclass to determine if a class is a vtype
        :return:
        """
        return True

    @classmethod
    def init_validator(cls):
        """
        Used by the metaclass to create the validator when the class is instantiated
        :return:
        """
        _vs = cls.__validators__
        if len(_vs) > 0:
            cls._validator = Validator(*_vs, help_msg=cls.__help_msg__, error_type=cls.__error_type__)

    def __init__(self):
        raise Exception("It does not make sense to instantiate a VType")

    @classmethod
    def assert_valid(cls,
                     name,  # type: str
                     val
                     ):
        """
        Class method that can be used to check if some value is valid. A name should be provided so that the
        error messages are human-friendly.

        :param name:
        :param val:
        :return:
        """
        # validate type
        validate(name, val, instance_of=cls.__types__, help_msg=cls.__help_msg__, error_type=cls.__error_type__)

        # apply validators
        if cls._validator is not None:
            cls._validator.assert_valid(name, val, help_msg=cls.__help_msg__, error_type=cls.__error_type__)

    # --- boolean checks (no exception) ---

    @classmethod
    def has_valid_type(cls, obj):
        # type: (...) -> bool
        """

        :param obj:
        :return:
        """
        return isinstance(obj, cls.__types__)

    @classmethod
    def has_valid_value(cls, obj):
        # type: (...) -> bool
        """

        :param obj:
        :return:
        """
        try:
            cls._validator.assert_valid('unnamed', obj)
        except (AttributeError,  # cls._validator is None
                ValidationError  # cls._validator is not None
                ):
            return False
        else:
            return True
