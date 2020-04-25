# Changelog

### 0.5.1 - packaging improvements

 - packaging improvements: set the "universal wheel" flag to 1, and cleaned up the `setup.py`. In particular removed dependency to `six` for setup and added `py.typed` file, as well as set the `zip_safe` flag to False. Removed tests folder from package. Fixes [#1](https://github.com/smarie/python-vtypes/issues/1)

### 0.5.0 - First public version

 * Validate both type and value with `isinstance`, thanks to easy-to-write "validating types"
 * `has_valid_type` and `has_valid_value` methods provided for easy auditing, as well as `is_vtype`
 * Validation syntax fully compliant with `valid8`. Compliant error message available through a `validate()` method
 * v-types are composable so that creating a library of reusable elements is straightforward (note: should we provide one in this library based on `valid8` [library](https://smarie.github.io/python-valid8/validation_funcs/b_base_validation_lib/) ?)  
 * Two styles: `vtype(...)` constructor method, as well as an alternate `class ...(VType)` style to perform composition using inheritance, and write docstrings more easily.
