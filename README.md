Robot Framework Tools
=====================

* A `testlibrary` framework for creating Dynamic Test Libraries.
* A `TestLibraryInspector`.
* An interactive `TestRobot`.
* A `robotshell` extension for IPython.

0. Installation
---------------

    python setup.py install

### Requirements

* [`python-moretools >= 0.1a23`](
    http://bitbucket.org/userzimmermann/python-moretools)
* [`robotframework >= 2.8`](http://robotframework.org)


1. Creating Dynamic Test Libraries
----------------------------------

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

The ``TestLibrary`` has no Keywords so far...
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
            # Maybe call some non-Keyword method as normal:
            self.no_keyword(...)
            ...

To get a simple interactive `SomeLibrary` overview just instantiate it:

    In : lib = SomeLibrary()

    In : lib.
    lib.SomeKeyword                lib.keyword
    lib.SomeOtherKeyword           lib.keywords
    lib.context_handlers           lib.no_keyword
    lib.get_keyword_arguments      lib.run_keyword
    lib.get_keyword_documentation  lib.session_handlers
    lib.get_keyword_names          lib.some_other_keyword

You can inspect all Keywords in Robot CamelCase style
(and call them for testing):

    In : lib.SomeKeyword
    Out: SomeLibrary.Some Keyword [ arg | *rest ]

### Keyword Options

When you apply custom decorators to your Keyword functions
which don't return the original function objects,
you would have to take care of preserving the original argspec for Robot.
`testlibrary` can handle this for you.
Just register your decorators as `custom_keyword_options`:

    def some_decorator(func):
        def wrapper(...):
            return func(...)

        # You still have to take care of the function(-->Keyword) name:
        wrapper.func_name = func.func_name
        return wrapper

    TestLibrary = testlibrary(
      custom_keyword_options=[
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
      custom_keyword_options=[
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
