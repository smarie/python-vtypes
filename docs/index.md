# `vtypes` - validating types

[![Python versions](https://img.shields.io/pypi/pyversions/vtypes.svg)](https://pypi.python.org/pypi/vtypes/) [![Build Status](https://travis-ci.org/smarie/python-vtypes.svg?branch=master)](https://travis-ci.org/smarie/python-vtypes) [![Tests Status](https://smarie.github.io/python-vtypes/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-vtypes/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-vtypes/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-vtypes)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-vtypes/) [![PyPI](https://img.shields.io/pypi/v/vtypes.svg)](https://pypi.python.org/pypi/vtypes/) [![Downloads](https://pepy.tech/badge/vtypes)](https://pepy.tech/project/vtypes) [![Downloads per week](https://pepy.tech/badge/vtypes/week)](https://pepy.tech/project/vtypes) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-vtypes.svg)](https://github.com/smarie/python-vtypes/stargazers)

*Validating types for python - use `isinstance()` to validate both type and value.*

`vtypes` is a small library to define "validating types". These types can be used to **add value validation on top of type checking** anywhere where you usually rely on `isinstance()`. This can in particular be used to make validation schemas simpler and more readable, for example used in [`pyfields`](https://smarie.github.io/python-pyfields/#3-autofields).


## Installing

```bash
> pip install vtypes
```

## Usage

### a - basics

A `VType` is a combination of :

 - a type **name**, for example `'PositiveInt'`
 - one or several **base types**: for example `int`.
 - one or several **validators**: for example `lambda x: x >= 0`

For example we can create a positive int:

```python
from vtypes import vtype

PositiveInt = vtype('PositiveInt', int, {'should be positive': lambda x: x >= 0})
```

A `VType`'s main purpose is to behave like a type (therefore to be compliant with `isinstance`) and to validate both type and values at the same time when `isinstance` is called:

```python
assert isinstance(1, PositiveInt)
assert not isinstance(-1, PositiveInt)
```

### b - goodies

In addition to this primary feature, a `VType` provides a few handy methods: 

 - detailed error messages with `validate` (note: a variable name should be provided, for example `'size'`).

```python
>>> PositiveInt.validate('size', -1)

ValidationError[ValueError]: Error validating [size=-1]. 
   InvalidValue: should be positive. 
   Function [<lambda>] returned [False] for value -1.
```

 - partial checkers: `has_valid_type` for type-only, and `has_valid_value` for value-only:
 
```python
assert PositiveInt.has_valid_type(-1)       # -1 is an int
assert not PositiveInt.has_valid_value(-1)  # -1 < 0
```

Finally, you may wish to use `is_vtype` to check if anything is a `VType`:

```python
from vtypes import is_vtype

assert is_vtype(PositiveInt)
assert not is_vtype(int)
assert not is_vtype(1)
```

### c - validators syntax

There are many ways to declare validators:
 
  - a single callable

  - a single tuple `(<callable>, <error_msg>)`, `(<callable>, <failure_type>)` or `(<callable>, <error_msg>, <failure_type>)`
  
  - a list of such callables and tuples
  
  - a **dictionary** where keys are `<callable>`, `<error_msg>`, or `<failure_type>` and values are one or two (tuple) of such elements. This is at least for the author, the most intuitive and readable style:

```python
ConstrainedInt = vtype('ConstrainedInt', int, 
                       {'should be positive': lambda x: x >= 0,
                        'should be a multiple of 3': lambda x: x % 3})
```
 
Note that this syntax is [`valid8` simple syntax](https://smarie.github.io/python-valid8/validation_funcs/c_simple_syntax/).

If you wish to create even more compact callables, you may wish to look at [`mini_lambda`](https://smarie.github.io/python-mini-lambda/).

### d - composition

You can combine types, for example a nonempty string can be obtained by mixing `NonEmpty` and `str`:

```python
NonEmpty = vtype('NonEmpty', (), {'should be non empty': lambda x: len(x) > 0})
"""A VType describing non-empty containers, with strictly positive length."""

NonEmptyStr = vtype('NonEmptyStr', (NonEmpty, str), ())
"""A VType for non-empty strings"""
```


### e - alternate coding style

An alternate way to define `VType`s is to define a python class inheriting from `VType`.

 - the validators can be provided as a class member named `__validators__`

 - the base type(s) can be either provided as superclass(es), or as a class member named `__type__`.

This provides an alternate style that developers might find handy in particular for entering docstrings and for making `VTypes` composition appear "just like normal python inheritance".

```python
from vtypes import VType

class NonEmpty(VType):
    """A VType describing non-empty containers, with strictly positive length.""" 
    __validators__ = {'should be non empty': lambda x: len(x) > 0}

class NonEmptyStr(NonEmpty, str):
    """A VType for non-empty strings"""

class AlternateNonEmptyStr(VType):
    """A VType for non-empty strings - alternate style"""
    __type__ = NonEmpty, str
```

The vtypes work as expected:

```python
assert isinstance('hoho', NonEmptyStr)
assert not isinstance('', NonEmptyStr)
assert not isinstance(1, NonEmptyStr)
```


## Main features

 * Validate both type and value with `isinstance`, thanks to easy-to-write "validating types"
 * `has_valid_type` and `has_valid_value` methods provided for easy auditing, as well as `is_vtype`
 * Validation syntax fully compliant with `valid8`. Compliant error message available through a `validate()` method
 * v-types are composable so that creating a library of reusable elements is straightforward (note: should we provide one in this library based on `valid8` [library](https://smarie.github.io/python-valid8/validation_funcs/b_base_validation_lib/) ?)  
 * Two styles: `vtype(...)` constructor method, as well as an alternate `class ...(VType)` style to perform composition using inheritance, and write docstrings more easily.

## See Also

 * [`checktypes`](https://gitlab.com/yahya-abou-imran/checktypes), that was a great source of inspiration. The only reason I ended up recreating something new a couple years after discovering it, was that I really wanted to leverage the `valid8` syntax for validators (as well as its standardized exceptions).
 
*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-vtypes](https://github.com/smarie/python-vtypes)
