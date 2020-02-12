#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  Copyright (c) Schneider Electric Industries, 2020. All right reserved.
from abc import ABCMeta
from inspect import currentframe, getmodule

from six import with_metaclass

try:
    from typing import Type, Union, Tuple, Iterable, Mapping, Optional, Any
    from valid8.common_syntax import ValidationFuncs, ValidationFuncDefinition, VFDefinitionElement
except ImportError:
    pass

from valid8 import validate
from valid8.common_syntax import FunctionDefinitionError
from valid8.entry_points import Validator, ValidationError


def _process_validators(validators  # type: ValidationFuncs
                        ):
    # type: (...) -> Tuple[Union[ValidationFuncDefinition, Mapping[VFDefinitionElement, Union[VFDefinitionElement, Tuple[VFDefinitionElement, ...]]]], ...]
    """
    Transforms validators into a tuple
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


class VTypeValidator(Validator):
    """
    Represents a `Validator` responsible to validate a `vtype`
    """
    __slots__ = '__weakref__', 'vtype'

    def __init__(self,
                 vtype,       # type: VTypeMeta
                 validators,  # type: ValidationFuncs
                 **kwargs
                 ):
        # store this additional info about the function been validated
        self.vtype = vtype

        super(VTypeValidator, self).__init__(*validators, **kwargs)


# class _TypesGetter(object):
#     """
#     A virtual property returning the __bases__ without the VType
#     """
#     def __get__(self, obj, owner):
#         return tuple(t for t in owner.__bases__ if t is not VType)
#
#
# types_getter = _TypesGetter()


class VTypeMeta(ABCMeta):
    """
    The metaclass for VTypes.

    It inherits from ABCMeta so that a VType can be registered as a virtual ancestor of anything.

    It implements `isinstance` according to the expected behaviour: an object is an instance of a VType if
     - it is an instance of all of its bases except VType (The __type__ virtual property contains the tuple of
       __bases__ without VType)
     - and it passes validation described by the __validators__

    When a class using this metaclass is created, various checks are made to ensure that users will not create VTypes
    with other contents than base types and validators.
    """
    ATTRS = ('__type__', '__validators__', '__help_msg__', '__error_type__', '__module__', '__qualname__', '__doc__')

    def __new__(mcls, name, bases, attrs):
        """
        Called when the new VType is created.

        :param name:
        :param bases:
        :param attrs:
        """
        try:
            # is mcls the original VType class ?
            VType
        except NameError:
            # yes: shortcut just create it
            return super(VTypeMeta, mcls).__new__(mcls, name, bases, attrs)
        else:
            # this is a new VType
            if not any(issubclass(b, VType) for b in bases):
                raise TypeError("It is not possible to create a VType without inheriting from `VType`. "
                                "Found %r" % (bases,))

            # remove VType from the bases if it is present
            # bases = tuple(b for b in bases if b is not VType)
            # NO --> we leave it so that subclass check works ; but we remove it when checking.

            # merge the __type__ and the bases to form the actual bases
            try:
                # is there a __type__ attribute on the class ?
                _types_ = attrs.pop('__type__')
            except KeyError:
                # no - only use the bases 'as is'
                pass
            else:
                # yes - make the type inherit from all of the __type__
                if isinstance(_types_, type):
                    bases = (_types_, ) + bases
                else:
                    bases = tuple(_types_) + bases

            # make sure that attrs does not contain anything else
            extra = set(attrs).difference(set(VTypeMeta.ATTRS))
            if len(extra) > 0:
                raise TypeError("a VType can not define any class attribute except for %r. Found: %r"
                                % (VTypeMeta.ATTRS, extra))

            # finally create the type
            # old: we remove everything from the bases
            # attrs['__type__'] = tuple(t for t in bases if t is not VType)
            # bases = (VType, )
            # the issue with doing this is that issubclass(PositiveInt, int) would *never* be able to work since it does
            # not call __subclasscheck__ on VTypeMeta but on the type of <int>.
            # of course we do not want to encourage users writing issubclass with VTypes, but since they are types one
            # day or another someone will do that ; since we have the choice let's use the less counter-intuitive
            # behaviour for is_subclass.

            # new: we put everything in the bases
            return super(VTypeMeta, mcls).__new__(mcls, name, bases, attrs)

    def __init__(cls,    # type: VTypeMeta
                 name,   # type: str
                 bases,
                 attrs):
        """
        Constructor for the VType. It initializes the embedded validator

        :param name:
        :param bases:
        :param attrs:
        """
        super(VTypeMeta, cls).__init__(name, bases, attrs)

        cls.init_vtype()

        # now all of these should be valid (removeds for speed)
        # assert '__type__' in cls.__dict__
        # assert '__validators__' in cls.__dict__
        # assert '_validator' in cls.__dict__

    def init_vtype(cls):
        """
        Used by the metaclass to create the validator when the class is instantiated.
        This method ensures that a created class has explicit `__type__`, `__validators__` and
        `_validator` fields so that inheritance from bases is bypassed.
        :return:
        """
        # assign a class property that will return the tuple of base types checked against
        # cls.__type__ = types_getter
        try:
            VType
        except NameError:
            # this is the VType type
            pass
        else:
            cls.__type__ = tuple(t for t in cls.__bases__ if t is not VType)

        # make sure the validators become an iterable
        try:
            # are there specific validators on this class ?
            _vs = cls.__dict__['__validators__']
        except KeyError:
            # no - nothing to do except creating an empty validators field
            cls.__validators__ = ()
            cls._validator = None
        else:
            # yes: make them a nice tuple and create the validator
            _vs = _process_validators(_vs)
            cls.__validators__ = _vs

            # create the associated validator
            if len(_vs) > 0:
                cls._validator = VTypeValidator(cls, _vs, help_msg=cls.__help_msg__, error_type=cls.__error_type__)
            else:
                cls._validator = None

    def __call__(cls, *args, **kwargs):
        """
        Constructors are disabled on VTypes

        :param args:
        :param kwargs:
        :return:
        """
        raise Exception("It does not make sense to instantiate a VType")

    # --------------- checkers

    def __instancecheck__(cls,  # type:  VTypeMeta
                          obj):
        """
        The 'core' of VType logic: instance check relies on both type and value

        :param obj:
        :return:
        """
        # first make sure that `obj` is an instance of all the base types
        if not all(isinstance(obj, t) for t in cls.__type__):
            return False

        # then validate the value with validators on this class
        return cls.has_valid_value(obj, inherited_validators=False)

    # def __subclasscheck__(cls,  # type:  VTypeMeta
    #                       subclass):
    #     """
    #     Nothing to implement here - all base types are defined as the bases of the class so the default implementation
    #     should be ok.
    #
    #     :param subclass:
    #     :return:
    #     """
    #     if not isinstance(subclass, VTypeMeta):
    #         return False
    #     elif len(cls.__type__) > 0:
    #         return issubclass(subclass, cls.__type__)
    #     else:
    #         return True

    def validate(cls,
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
        for typ in cls.__type__:
            validate(name, val, instance_of=typ, help_msg=cls.__help_msg__, error_type=cls.__error_type__)

        # apply validators
        if cls._validator is not None:
            cls._validator.assert_valid(name, val, help_msg=cls.__help_msg__, error_type=cls.__error_type__)

    # --- boolean checks (no exception) ---

    # not very interesting now that in the type bases there can be value checkers

    def has_valid_type(cls, obj):
        # type: (...) -> bool
        """
        Returns `True` if `obj` has a valid type according to the `__types__` in this `VType`.
        More precisely, for all classes in this class' `__types__` (=bases),

         - if this class `t` is a `VType`, t.has_valid_type(obj) should return True
         - otherwise, `isinstance(obj, t)` should return True

        :param obj:
        :return:
        """
        # should be an instance of all base types
        # for VTypes, we rely on has_valid_type instead of isinstance to avoid value check
        for t in cls.__type__:
            # if t is VType:
            #     continue
            if isinstance(t, VTypeMeta):
                if not t.has_valid_type(obj):
                    return False
            elif not isinstance(obj, t):
                return False
            else:
                continue
        return True

    def has_valid_value(cls,
                        obj,
                        inherited_validators=True  # type: bool
                        ):
        # type: (...) -> bool
        """
        Returns True if `obj` is valid according to the `__validators__` on this class and in all the VTypes in its
        `__types__` (ancestor classes). You may turn `inherited_validators=False` to only check local validators.

        :param obj: the object to validate
        :param inherited_validators: an optional boolean. If this is `True` (default), `has_valid_value` will also be
            called on all ancestor VType classes and `True` will be returned only if all return `True`. Setting `False`
            will only use the local `__validators__` on this class.
        :return:
        """
        if cls._validator is not None:
            try:
                cls._validator.assert_valid('unnamed', obj)
            except ValidationError:
                return False

        if inherited_validators:
            for t in cls.__type__:
                # if t is VType:
                #     continue
                if isinstance(t, VTypeMeta) and not t.has_valid_value(obj, inherited_validators=True):
                    return False
                else:
                    continue

        return True


class VType(with_metaclass(VTypeMeta, object)):
    """
    The super class of all `VType`s.

    When a class inherits from `VType`, it is manipulated by the `VTypeMeta` metaclass upon creation
    so that its `__type__` and `__validators__` represent the synthesis of all of its ancestors.

    Also at class creation time a `VTypeValidator` instance is created, that will be used in all subsequent checks.
    Therefore if you dynamically update `__validators__`, you should explicitly call `cls.init_vtype()` to refresh
    the validator associated with the class.
    """
    __type__ = ()          # type: Union[Type, Tuple[Type]]
    __validators__ = ()    # type: ValidationFuncs
    __error_type__ = None  # type: Type[ValidationError]
    __help_msg__ = None    # type: str

    _validator = None      # type: Validator

    # @classmethod
    # def init_vtype(cls):

    def __init__(self):
        raise Exception("It does not make sense to instantiate a VType")

    # @classmethod
    # def assert_valid(cls,
    #                  name,  # type: str
    #                  val
    #                  ):

    # # --- boolean checks (no exception) ---
    #
    # @classmethod
    # def has_valid_type(cls, obj):
    #
    # @classmethod
    # def has_valid_value(cls, obj):


# noinspection PyShadowingBuiltins
def vtype(name,             # type: str
          base=(),          # type: Union[Type, Tuple[Type]]
          validators=(),    # type: ValidationFuncs
          help_msg=None,    # type: str
          error_type=None,  # type: Type[ValidationError]
          doc=None          # type: str
          ):
    # type: (...) -> Union[Type[VType], VTypeMeta]
    """
    Creates a new Validating Type, a subclass of VType.

    :param name: the name for the VType to create
    :param base: an optional type or tuple of types that will be used for type checking with `isinstance()`.
    :param validators: an optional validator or group of validators, following the valid8 syntax (either a callable,
        tuple, list, or dict).
    :param help_msg: an optional help message (a string) for the validation errors
    :param error_type: an optional error type (a subtype of `ValidationError`) for the validation errors
    :param doc: an optional docstring
    :return:
    """
    new_type = VTypeMeta(name, (VType,), dict(__type__=base, __validators__=validators,
                                              __help_msg__=help_msg, __error_type__=error_type))
    new_type.__module__ = get_caller_module().__name__
    if doc is not None:
        new_type.__doc__ = doc
    return new_type


def get_caller_module(frame_offset=1):
    # grab context from the caller frame
    frame = _get_callerframe(offset=frame_offset)
    return getmodule(frame)


def _get_callerframe(offset=0):
    # inspect.stack is extremely slow, the fastest is sys._getframe or inspect.currentframe().
    # See https://gist.github.com/JettJones/c236494013f22723c1822126df944b12
    # frame = sys._getframe(2 + offset)
    frame = currentframe()
    for _ in range(2 + offset):
        frame = frame.f_back
    return frame


def is_vtype(t  # type: Any
             ):
    # type: (...) -> bool
    """
    Returns `True` if `t` is a `VType`, `False` otherwise.
    It is equivalent to `isinstance(t, VTypeMeta)` or `issubclass(t, VType)`, with exception catching.

    :param t:
    :return:
    """
    # noinspection PyBroadException
    try:
        return isinstance(t, VTypeMeta)
    except Exception:
        return False
