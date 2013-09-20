Robot Framework Tools
=====================

* A [`testlibrary`][1] framework for creating Dynamic Test Libraries.

* A [`TestLibraryInspector`][2].

* An interactive [`TestRobot`][3].

* A [`robotshell`][4] extension for IPython.


0. Installation
---------------

    python setup.py install

Or with [pip](http://www.pip-installer.org):

    pip install .

Or from [PyPI](https://pypi.python.org/pypi/robotframework-tools):

    pip install robotframework-tools

### Requirements

* [`moretools >= 0.1a25`](
    http://bitbucket.org/userzimmermann/python-moretools)

* [`robotframework >= 2.8`](http://robotframework.org)


1. Creating Dynamic Test Libraries
----------------------------------
[1]: #markdown-header-1-creating-dynamic-test-libraries

    from robottools import testlibrary

    TestLibrary = testlibrary()

Defined in a module also called `TestLibrary`,
this generated Dynamic `TestLibrary` type
could now directly be imported in Robot Framework.
It features all the required methods:

* `get_keyword_names`
* `get_keyword_arguments`
* `get_keyword_documentation`
* `run_keyword`

### Keywords

The `TestLibrary` has no Keywords so far...
To add some just use the `TestLibrary.keyword` decorator:

    @TestLibrary.keyword
    def some_keyword(self, arg, *rest):
        ...

A keyword function can be defined anywhere in any scope.
The `TestLibrary.keyword` decorator
always links it to the `TestLibrary`
(but always returns the original function object).
And when called as a Keyword from Robot Framework
the `self` parameter will always get the `TestLibrary` instance.

You may want to define your keyword methods
at your Test Library class scope.
Just derive your actual Dynamic Test Library class from `TestLibrary`:

    # SomeLibrary.py

    class SomeLibrary(TestLibrary):
        def no_keyword(self, ...):
            ...

        @TestLibrary.keyword
        def some_other_keyword(self, arg, *rest):
            ...

To get a simple interactive `SomeLibrary` overview just instantiate it:

    In : lib = SomeLibrary()

You can inspect all Keywords in Robot CamelCase style
(and call them for testing):

    In : lib.SomeKeyword
    Out: SomeLibrary.Some Keyword [ arg | *rest ]

### Keyword Options

When you apply custom decorators to your Keyword functions
which don't return the original function objects,
you would have to take care of preserving the original argspec for Robot.
`testlibrary` can handle this for you:

    def some_decorator(func):
        def wrapper(...):
            return func(...)

        # You still have to take care of the function(-->Keyword) name:
        wrapper.func_name = func.func_name
        return wrapper

    TestLibrary = testlibrary(
      register_keyword_options=[
        # Either just:
        some_decorator,
        # Or with some other name:
        ('some_option', some_decorator),
        ],
      )

    @TestLibrary.keyword.some_option
    def some_keyword_with_options(self, arg, *rest):
        ...

There are predefined options. Currently:

* `unicode_to_str` - Convert all `unicode` args (Robot's default) to `str`

You can specify `default_keyword_options` that will always be applied:

    TestLibrary = testlibrary(
      register_keyword_options=[
        ('some_option', some_decorator),
        ],
      default_keyword_options=[
        'unicode_to_str',
        'some_option',
      )

To bypass the `default_keyword_options` for single Keywords:

    @TestLibrary.keyword.no_options
    def some_keyword_without_options(self, arg, *rest):
        ...

    @TestLibrary.keyword.reset_options.some_option
    def some_keyword_without_default_options(self, arg, *rest):
        ...


2. Inspecting Test Libraries
----------------------------
[2]: #markdown-header-2-inspecting-test-libraries

    from robottools import TestLibraryInspector

Now you can load any Test Library in two ways:

    builtin = TestLibraryInspector('BuiltIn')
    oslib = TestLibraryInspector.OperatingSystem


3. Using Robot Framework interactively
--------------------------------------
[3]: #markdown-header-3-using-robot-framework-interactively

    from robottools import TestRobot

    test = TestRobot('Test')

The `TestRobot` basically uses the same Robot Framework internals
for loading Test Libraries and running Keywords
as `pybot` and its alternatives,
so you can expect the same behavior from your Keywords.

All functionalitiy is exposed in CamelCase:

    test.Import('SomeLibrary')


4. Using IPython as a Robot Framework shell
-------------------------------------------
[4]: #markdown-header-4-using-ipython-as-a-robot-framework-shell

    In : %load_ext robotshell

Now all the `robottools.TestRobot` functionality
is exposed as IPython magic functions...

    [Robot.Default]
    In : %Import SomeLibrary
    Out: [Library] SomeLibrary

As with a `robottools.TestRobot` you can call Keywords
with or without the Test Library prefix.
You can simply assign the return values to normal Python variables.
And there are two ways of separating the arguments:

    [Robot.Default]
    In : ret = %SomeKeyword value ...
    [TRACE] Arguments: [ 'value', '...' ]
    [TRACE] Return: ...

    [Robot.Default]
    In : ret = %SomeLibrary.SomeOtherKeyword | with some value | ...
    [TRACE] Arguments: [ 'with some value', '...' ]
    [TRACE] Return: ...

You can create new `Robot`s and switch between them:

    [Robot.Default]
    In : %Robot Test
    Out: [Robot] Test

    [Robot.Test]
    In : %Robot.Default
    Out: [Robot] Default

    [Robot.Default]
    In :

If a Keyword fails the traceback is just printed like in a Robot Log.
If it fails unexpectedly you may want to debug it.
Just turn on `%robot_debug` mode
and the Keyword's exception will be re-raised.
Combine it with IPython's automatic `%pdb` mode
and you'll get a nice Test Library debugging environment.
