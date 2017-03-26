"""Support for parameterizing test methods in a unittest TestCase.

This module provides two decorators and a constructor: a class decorator named
'parameterizable', a method decorator named 'parameters', and a parameter list
constructor named C (short for  'call specification').  In order for the
parameters decorator to do anything useful, the test class must be decorated
with the parameterizable decorator.

parameterizable is a simple class decorator that takes no arguments.

Parameter list specifications are simply parameter lists passed to the
constructor C.  Thus, if we want to pass two positional arguments to our
parameterized test, we write:

    C(1, 2)

If we also want to pass the keyword argument 'foo', we write:

    C(1, 2, foo=3)

Parameter list specifications can be passed to the parameters decorator as
positional arguments, as keyword arguments, or as single argument lists or
dicts.  That is, all of the following result in the specified parameters being
passed to the decorated test function:

    @parameters(C(1, 2), C(3, 4, bar=7))
    params = [C(1, 2), C(3, 4, bar=7)]
    @parameters(params)
    @parameters(*params)

    @parameters(dict(test1=C(1, 2), test2=C(3, 4, bar=7)))
    params = dict(test1=C(1, 2), test2=C(3, 4, bar=7))
    @parameters(params)
    @parameters(**params)

The reason all of these forms is supported is that it is more natural to use
positional or keyword arguments when using a single set of parameter lists for
a single test function, while it is more natural to pass s single argument list
or dict to the parameters decorator when the same set of parameter lists is
being passed to more than one test.

The difference between positional arguments or a list, and keyword arguments
or a dict, is in how the test names are generated.  If the above parameter
lists were being used to decorate a test function named 'test_foo',
the first set above would generate tests named:

    test_foo_1_2
    test_foo_3_4__bar_7

while the second set above would generate tests named:

    test_foo_test1
    test_foo_test2

Generated test names can be specified on the unittest command line to invoke
that particular test, as long as the generated test name is a valid python
identifier.  (Note that under Python 3.3, 3.4, and 3.5, in order to get stable
auto-generated names if there are multiple keyword arguments, you will need to
set PYTHONHASHSEED, because otherwise the keyword parameters could be in a
different order in the name from run to run.)

You can also specify the special keyword argument _include_key to
@parameterize, in which case the key that names the parameter list is passed as
the first non-self argument to the test:

    @parameters(a=C(1, 2), b=C(3, 4), _include_key=True)
    def test_foo(self, key, arg1, arg2):
        pass

key here will be 'a' when arg1 and arg2 are (1, 2), and 'b' when they are (3,
4).

"""

from functools import wraps


valid_settings = ['_include_key']


class C:

    """Specify a parameter list to be later passed to a function."""

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def name(self):
        normalize = lambda x: str(x).replace(' ', '_')
        args = '_'.join(normalize(x) for x in self.args)
        kw = '__'.join(n + '_' + normalize(k) for n, k in self.kw.items())
        return '__'.join(filter(None, (args, kw)))

    def prepend_positional(self, value):
        self.args = (value,) + self.args

    def invoke(self, func):
        return func(*self.args, **self.kw)


def parameters(*args, **kw):
    """Create a test call to decorated func for each supplied parameter list.

    See module docstring for details on how to specify parameter lists.  The
    class must be decorated with @paremteriable.
    """
    settings = {}
    if len(args) == 1 and not hasattr(args[0], 'invoke'):
        args = args[0]
        if hasattr(args, 'items'):
            kw.update(args)
            args = ()
    for name in list(kw):
        if name.startswith('_'):
            if name not in valid_settings:
                raise TypeError("Invalid setting name {}".format(name))
            settings[name] = kw.pop(name)
    for arg in args:
        name = arg.name()
        if name in kw:
            raise NameError("Positional synthetic name collides with",
                            " keyword name")
        kw[name] = arg
    def parameterize_decorator(func):
        func._parameterized_ = True
        func._parameters_ = kw
        func._settings_ = settings
        return func
    return parameterize_decorator


def parameterizable(cls):
    """Turn each function decorated with @parameters into a series of tests.

    Each generated test function should call the decorated function with one of
    the lists of parameters passed in to the decorator.  See the module
    docstring for details.
    """
    for name, attr in list(cls.__dict__.items()):
        if hasattr(attr, '_parameterized_'):
            parameters = attr._parameters_
            if attr._settings_.get('_include_key'):
                for k, v in parameters.items():
                    parameters[k].prepend_positional(k)
            impl_name = '__' + name
            delattr(cls, name)
            setattr(cls, impl_name, attr)
            for paramsname, call_spec in parameters.items():
                test = (lambda self, impl_name=impl_name, call_spec=call_spec:
                                call_spec.invoke(getattr(self, impl_name)))
                test.__name__ = name + '_' + paramsname
                setattr(cls, test.__name__, test)
    return cls
