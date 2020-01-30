# python validating types (vtypes)

[![Python versions](https://img.shields.io/pypi/pyversions/vtypes.svg)](https://pypi.python.org/pypi/vtypes/) [![Build Status](https://travis-ci.org/smarie/python-vtypes.svg?branch=master)](https://travis-ci.org/smarie/python-vtypes) [![Tests Status](https://smarie.github.io/python-vtypes/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-vtypes/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-vtypes/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-vtypes)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-vtypes/) [![PyPI](https://img.shields.io/pypi/v/vtypes.svg)](https://pypi.python.org/pypi/vtypes/) [![Downloads](https://pepy.tech/badge/vtypes)](https://pepy.tech/project/vtypes) [![Downloads per week](https://pepy.tech/badge/vtypes/week)](https://pepy.tech/project/vtypes) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-vtypes.svg)](https://github.com/smarie/python-vtypes/stargazers)

*Validating types for python - use `isinstance()` to validate both type and value.*

`vtypes` is a small library to define "validating types". These types can be used to add value validation on top of type checking anywhere where you usually rely on `isinstance()`. This can in particular be used to make validation schemas simpler and more readable, for example used in [`pyfields`](https://smarie.github.io/python-pyfields/#3-autofields).


## Installing

```bash
> pip install vtypes
```

## Usage

### a - basics

You create a `VType` by combining one or several base types with optional value validators following the [`valid8` simple syntax](https://smarie.github.io/python-valid8/validation_funcs/c_simple_syntax/).

For example we can create a positive int:

```python
from vtypes import vtype

PositiveInt = vtype('PositiveInt', int, {'should be positive': lambda x: x >= 0})
```

`isinstance` works as expected:

```python
assert isinstance(1, PositiveInt)
assert not isinstance(-1, PositiveInt)
```

You can also get a more detailed error if you wish:

```python
>>> PositiveInt.assert_valid('x', -1)
ValidationError[ValueError]: Error validating [x=-1]. 
   InvalidValue: should be positive. Function [<lambda>] returned [False] for value -1.
```

### b - composition

You can combine types, for example a positive int can be obtained by mixing `Positive` and `int`:

```python
TODO
```


## Main features

 * **TODO**

## See Also

 * [`checktypes`](https://gitlab.com/yahya-abou-imran/checktypes), that was a great source of inspiration. The only reason for recreating something new was the capability to use the `valid8` syntax for validators (as well as its standardized exceptions).
 
*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-vtypes](https://github.com/smarie/python-vtypes)
