Parameterizing Tests Using the stdlib unittest
==============================================


Test parameterization is an often-requested feature.  Support for it has been
added to Nose via plugin, and py.test supports it.  But if for some reason you
need to stick with the standard library unittest framework, it has no built in
way to do this.  This module is essentially a proposal for how to add this
feature to the stdlib.

You can install the package by hand by just copying the module to an
appropriate location, or you can install it using pip.


Usage
-----

This module provides two decorators and a constructor: a class decorator named
``parameterizable``, a method decorator named ``parameters``, and a parameter
list constructor named ``C`` (short for 'call specification').  In order for
the ``parameters`` decorator to do anything useful, the test class must be
decorated with the ``parameterizable`` decorator.

``parameterizable`` is a simple class decorator that takes no arguments.

Parameter list specifications are normal function call arguments, passed to the
constructor ``C``.  Thus, if we want to pass two positional arguments to our
parameterized test, we write::

    C(1, 2)

If we also want to pass the keyword argument ``foo``, we write::

    C(1, 2, foo=3)

Parameter list specifications can be passed to the ``parameters`` decorator as
positional arguments, as keyword arguments, or as single argument lists or
dicts.  That is, all of the following result in the specified parameters being
passed to the decorated test function::

    @parameters(C(1, 2), C(3, 4, bar=7))
    params = [C(1, 2), C(3, 4, bar=7)]
    @parameters(params)
    @parameters(*params)

    @parameters(dict(test1=C(1, 2), test2=C(3, 4, bar=7)))
    params = dict(test1=C(1, 2), test2=C(3, 4, bar=7))
    @parameters(params)
    @parameters(**params)

The reason all of these forms is supported is that it is more natural to pass
positional or keyword arguments to ``parameters`` when providing parameter
list specifications for a single test function, while it is more natural to
pass a single-argument list or dict to ``parameters`` when a set of parameter
list specifications is being re-used with multiple tests.

The difference between positional arguments (or a list), and keyword arguments
(or a dict), is in how the test names are generated.  In the keyword argument
(or dictionary) form, the keyword/key is used to complete the test name.  In
the positional argument (or list) form, the values of the arguments are
stringified, and the values (and the keywords in the call specification, if
any) are used to complete the test name.  We refer to these as 'auto-generated
names'.

If the above parameter lists were being used to decorate a test function named
``test_foo``, the first set above would generate tests named::

    test_foo_1_2
    test_foo_3_4__bar_7

while the second set above would generate tests named::

    test_foo_test1
    test_foo_test2

The generated test names can be specified on the unittest command line to
invoke that particular test.  For auto-generated names, this works only if the
auto-generated name is a valid python identifier.  Note that under Python 3.3,
3.4, and 3.5 in order to get stable auto-generated names if there are multiple
keyword arguments you will need to set PYTHONHASHSEED, because otherwise the
keyword parameters could be in a different order in the name from run to run.

You can also specify the special keyword argument ``_include_key`` to
``parameters``, in which case the key that names the parameter list
specification is passed as the first non-self argument to the test::

    @parameters(a=C(1, 2), b=C(3, 4), _include_key=True)
    def test_foo(self, key, arg1, arg2):
        pass

``key`` here will be ``a`` when ``arg1`` and ``arg2`` are ``(1, 2)``, and ``b``
when they are ``(3, 4)``.

All other keyword names starting with ``_`` are reserved, so such names cannot
be used as parameter list specification names.
