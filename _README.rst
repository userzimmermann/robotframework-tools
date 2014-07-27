
robotframework-tools
====================

.. sourcecode:: python

    import robottools
    print(robottools.__version__)

.. parsed-literal::

    0.1a109-61


.. sourcecode:: python

    print(robottools.__description__)

.. parsed-literal::

    Python Tools for Robot Framework and Test Libraries.


-  A testlibrary_ framework for creating Dynamic Test
   Libraries.

-  A [``ContextHandler``\ ][1.1] framework for ``testlibrary`` to create
   switchable sets of different Keyword implementations.

-  A [``SessionHandler``\ ][1.2] framework for ``testlibrary`` to
   auto-generate Keywords for session management.

-  A [``TestLibraryInspector``\ ][2].

-  An interactive [``TestRobot``\ ][3].

-  A [``RemoteRobot``\ ][4], combining ``TestRobot`` with external
   ```RobotRemoteServer`` <https://pypi.python.org/pypi/robotremoteserver>`__

-  A [``ToolsLibrary``\ ][5], accompanying Robot Framework's standard
   Test Libraries.

-  A [``robotshell``\ ][6] extension for
   `IPython <http://ipython.org>`__.

https://bitbucket.org/userzimmermann/robotframework-tools

https://github.com/userzimmermann/robotframework-tools

0. Setup
========

**Supported Python versions**: `2.7 <http://docs.python.org/2.7>`__,
`3.3 <http://docs.python.org/3.3>`__,
`3.4 <http://docs.python.org/3.4>`__

Just install the latest
`release <https://pypi.python.org/pypi/modeled>`__ with
`pip <http://www.pip-installer.org>`__. It automatically installs
requirements:

::

    pip install robotframework-tools

.. sourcecode:: python

    robottools.__requires__



.. parsed-literal::

    six
    path.py
    moretools>=0.1a38



-  **Python 2.7**: ``robotframework>=2.8``

-  **Python 3.x**: ``robotframework-python3>=2.8.4``

.. sourcecode:: python

    robottools.__extras__



.. parsed-literal::

    [remote]
    robotremoteserver
    
    [robotshell]
    ipython



To install with all extra requirements:

::

    pip install robotframework-tools[all]

This ``README.ipynb`` will also be installed. Just copy it:

.. sourcecode:: python

    # robottools.__notebook__.copy('path/name.ipynb')

.. _testlibrary:
1. Creating Dynamic Test Libraries
==================================

.. sourcecode:: python

    from robottools import testlibrary
.. sourcecode:: python

    TestLibrary = testlibrary()
This generated Dynamic ``TestLibrary`` class could now directly be
imported in Robot Framework. It features all the Dynamic API methods:

-  ``get_keyword_names``
-  ``get_keyword_arguments``
-  ``get_keyword_documentation``
-  ``run_keyword``

Keywords
~~~~~~~~

The ``TestLibrary`` has no Keywords so far... To add some just use the
``TestLibrary.keyword`` decorator:

.. sourcecode:: python

    @TestLibrary.keyword
    def some_keyword(self, arg, *rest):
        pass
A keyword function can be defined anywhere in any scope. The
``TestLibrary.keyword`` decorator always links it to the ``TestLibrary``
(but always returns the original function object). And when called as a
Keyword from Robot Framework the ``self`` parameter will always get the
``TestLibrary`` instance.

You may want to define your keyword methods at your Test Library class
scope. Just derive your actual Dynamic Test Library class from
``TestLibrary``:

.. sourcecode:: python

    class SomeLibrary(TestLibrary):
        def no_keyword(self, *args):
            pass
    
        @TestLibrary.keyword
        def some_other_keyword(self, *args):
            pass
To get a simple interactive ``SomeLibrary`` overview just instantiate
it:

.. sourcecode:: python

    lib = SomeLibrary()
You can inspect all Keywords in Robot CamelCase style (and call them for
testing):

.. sourcecode:: python

    lib.SomeKeyword



.. parsed-literal::

    SomeLibrary.Some Keyword [ arg | *rest ]



By default the Keyword names and argument lists are auto-generated from
the function definition. You can override that:

.. sourcecode:: python

    @TestLibrary.keyword(name='KEYword N@me', args=['f|r$t', 'se[ond'])
    def function(self, *args):
        pass
Keyword Options
~~~~~~~~~~~~~~~

When you apply custom decorators to your Keyword functions which don't
return the original function objects, you would have to take care of
preserving the original argspec for Robot. ``testlibrary`` can handle
this for you:

.. sourcecode:: python

    def some_decorator(func):
        def wrapper(self, *args):
            return func(self, *args)
    
        # You still have to take care of the function(-->Keyword) name:
        wrapper.__name__ = func.__name__
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
        pass
There are predefined options. Currently:

-  ``unicode_to_str`` - Convert all ``unicode`` values (pybot's default)
   to ``str``.

You can specify ``default_keyword_options`` that will always be applied:

.. sourcecode:: python

    TestLibrary = testlibrary(
      register_keyword_options=[
        ('some_option', some_decorator),
        ],
      default_keyword_options=[
        'unicode_to_str',
        'some_option',
        ],
      )
To bypass the ``default_keyword_options`` for single Keywords:

.. sourcecode:: python

    @TestLibrary.keyword.no_options
    def some_keyword_without_options(self, arg, *rest):
        pass
    
    @TestLibrary.keyword.reset_options.some_option
    def some_keyword_without_default_options(self, arg, *rest):
        pass
