Robot Framework Tools
=====================

[Python](http://python.org) Tools for [Robot Framework](
  http://robotframework.org) and Test Libraries.

* A [`testlibrary`][1] framework for creating Dynamic Test Libraries.

* A [`ContextHandler`][1.1] framework for `testlibrary`
  to create switchable sets of different Keyword implementations.

* A [`SessionHandler`][1.2] framework for `testlibrary`
  to auto-generate Keywords for session management.

* A [`TestLibraryInspector`][2].

* An interactive [`TestRobot`][3].

* A [`RemoteRobot`][4], combining `TestRobot`
  with external [`RobotRemoteServer`](
    https://pypi.python.org/pypi/robotremoteserver)

* A [`ToolsLibrary`][5],
  accompanying Robot Framework's standard Test Libraries.

* A [`robotshell`][6] extension for [IPython](http://ipython.org).


# 0. Setup
----------

Supported __Python__ versions: __2.7.x__, __3.3.x__ and later

Package name: __robotframework-tools__

Package extra features:

* __[remote]__: `RemoteRobot`
* __[robotshell]__

### Requirements

* [`six>=1.10`](https://pypi.python.org/pypi/six)
* [`path.py>=8.0`](https://pypi.python.org/pypi/path.py)
* [`moretools>=0.1.8`](https://pypi.python.org/pypi/moretools)
* [`robotframework>=2.8.7`](https://pypi.python.org/pypi/robotframework)
* __Python 3.x__: 
  * Robot Framework 3.0+ is officially Python 3 compatible
  * For earlier versions please install [`robotframework-python3`](
      https://pypi.python.org/pypi/robotframework-python3)

Extra requirements for __[remote]__:

* [`robotremoteserver`](https://pypi.python.org/pypi/robotremoteserver)

Extra requirements for __[robotshell]__:

* [`ipython>=4.0`](https://pypi.python.org/pypi/ipython)

### Installation

    python setup.py install

Or with [pip](http://www.pip-installer.org):

    pip install .

Or from [PyPI](https://pypi.python.org/pypi/robotframework-tools):

    pip install robotframework-tools

* With all extra features:

        pip install robotframework-tools[remote,robotshell]

* Robot Framework will not be installed automatically


# 1. Creating Dynamic Test Libraries
------------------------------------
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

By default the Keyword names and argument lists are auto-generated
from the function definition.
You can override that:

    @TestLibrary.keyword(name='KEYword N@me', args=['f|r$t', 'se[ond', ...])
    def function(self, *args):
        ...

### Keyword Options

When you apply custom decorators to your Keyword functions
which don't return the original function objects,
you would have to take care of preserving the original argspec for Robot.
`testlibrary` can handle this for you:

    def some_decorator(func):
        def wrapper(...):
            return func(...)

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
        ...

There are predefined options. Currently:

* `unicode_to_str` - Converts all `unicode` values (pybot's default) to `str`.
* `varargs_to_kwargs` - Moves items pairwise from `*varargs` to `**kwargs`.
* `kwargs_from_strings` - Splits any `key=value` strings in `*varargs`
  and moves them to `**kwargs`.
* `keys_from_vars` - Substitutes variable keys in `${key}=value` items
  in `**kwargs`.

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


## 1.1 Adding switchable Keyword contexts
-----------------------------------------
[1.1]: #markdown-header-11-adding-switchable-keyword-contexts

    from robottools import ContextHandler

TODO...


## 1.2 Adding session management
--------------------------------
[1.2]: #markdown-header-12-adding-session-management

    from robottools import SessionHandler

Whenever your Test Library needs to deal with sessions,
like network connections,
which you want to open, switch, close,
and when you don't always want to specify
the actual session to use as a Keyword argument,
just do:

    class SomeConnection(SessionHandler):
        # All methods starting with `open`
        # will be turned into session opener Keywords.
        # `self` will get the Test Library instance.
        def open(self, host, *args):
            return internal_connection_handler(host)

        def open_in_a_different_way(self, host):
            return ...

    TestLibrary = testlibrary(
      session_handlers=[SomeConnection],
      )

The following Keywords will be generated:

* `TestLibrary.Open Some Connection [ host | *args ]`
* `TestLibrary.Open Named Some Connection [ alias | host | *args ]`
* `TestLibrary.Open Some Connection In A Different Way [ host ]`
* `TestLibrary.Open Named Some Connection In A Different Way [ alias | host ]`
* `TestLibrary.Swith Some Connection [ alias ]`
* `TestLibrary.Close Some Connection [ ]`

You can access the currently active session instance,
as returned from an opener Keyword,
with an auto-generated property based on the handler class name:

    @TestLibrary.keyword
    def some_keyword(self):
        self.some_connection.do_something()

If there is no active session,
a `TestLibrary.SomeConnectionError` will be raised.

`Close Some Connection` will only release all references
to the stored session object.
To add custom logic just add a `close` method to your `SessionHandler`:

    class SomeConnection(SessionHandler):
        ...

        def close(self, connection):
            # `self` will get the Test Library instance.
            ...

The `SessionHandler` framework additionally supports some `Meta` options:

    class SomeConnection(SessionHandler):
        class Meta:
            # options
            ...

* `auto_explicit = True` will automatically modify
  every Keyword of the Test Library to support explicit session switching
  with an additional named argument based on the handler class name.
  After the Keyword call, the session will switch back
  to the previously active one:

  `Some Keyword    ...   some_connection=alias`


# 2. Inspecting Test Libraries
------------------------------
[2]: #markdown-header-2-inspecting-test-libraries

    from robottools import TestLibraryInspector

Now you can load any Test Library in two ways:

    builtin = TestLibraryInspector('BuiltIn')
    oslib = TestLibraryInspector.OperatingSystem

TODO...


# 3. Using Robot Framework interactively
----------------------------------------
[3]: #markdown-header-3-using-robot-framework-interactively

    from robottools import TestRobot

    test = TestRobot('Test')

The `TestRobot` basically uses the same Robot Framework internals
for loading Test Libraries and running Keywords
as `pybot` and its alternatives,
so you can expect the same behavior from your Keywords.

All functionalitiy is exposed in CamelCase:

    test.Import('SomeLibrary')

TODO...


# 4. Using Robot Framework remotely
-----------------------------------
[4]: #markdown-header-4-using-robot-framework-remotely

    from robottools.remote import RemoteRobot

`RemoteRobot` is derived from `robottools.TestRobot`
and external `robotremoteserver.RobotRemoteServer`,
which is derived from Python's `SimpleXMLRPCServer`.
The `__init__()` method shares most of its basic arguments
with `RobotRemoteServer`:

    def __init__(
      self, libraries, host='127.0.0.1', port=8270, port_file=None,
      allow_stop=True, allow_import=None,
      register_keywords=True, introspection=True,
      ):
        ...

The differences:

* Instead of a single pre-initialized Test Library instance,
  you can provide a sequence of multiple Test Library names,
  which will be imported and initialized using `TestRobot.Import()`.
* The additional argument `allow_import`
  takes a sequence of Test Library names,
  which can later be imported remotely
  via the `Import Remote Library` Keyword described below.
* `RemoteRobot` also directly registers Keywords as remote methods
  (`RobotRemoteServer` only registers a __Dynamic Library API__).
  You can change this by setting `register_keywords=False`.
* `RemoteRobot` calls `SimpleXMLRPCServer.register_introspection_functions()`.
  You can change this by setting `introspection=False`.

Once initialized the `RemoteRobot` will immediately start its service.
You can connect with any XML-RPC client
like Python's `xmlrpc.client.ServerProxy`
(__Python 2.7__: `xmlrpclib.ServerProxy`).

To access the `RemoteRobot` from your Test Scripts,
you can use Robot Framework's standard `Remote` Library.
Once connected it will provide all the Keywords from the Test Libraries
imported by the `RemoteRobot`.

Besides `RobotRemoteServer`'s additional `Stop Remote Server` Keyword
`RemoteRobot` further provides these extra Keywords:

* `Import Remote Library [ name ]`

  >Remotely import the Test Library with given `name`.
  >
  >Does the same remotely as `BuiltIn.Import Library` does locally.
  >The Test Library must be allowed on server side.
  >
  >The `Remote` client library must be reloaded
  >to make the new Keywords accessible.
  >This can be done with `ToolsLibrary.Reload Library`.


# 5. Using the ToolsLibrary
---------------------------
[5]: #markdown-header-5-using-the-toolslibrary

The `ToolsLibrary` is a Dynamic Test Library,
which provides these additional general purpose Keywords:

* `Reload Library [ name | *args]`

  >Reload an already imported Test Library
  >with given `name` and optional `args`.
  >
  >This also leads to a reload of the Test Library Keywords,
  >which allows Test Libraries to dynamically extend or change them.

The `ToolsLibrary` is based on `robottools.testlibrary`.
To use it directly in __Python__:

    from ToolsLibrary import ToolsLibrary

    tools = ToolsLibrary()

Then you can call the Keywords in `tools.CamelCase(...)` style.


# 6. Using IPython as a Robot Framework shell
---------------------------------------------
[6]: #markdown-header-6-using-ipython-as-a-robot-framework-shell

    In : %load_ext robotshell

Now all the `robottools.TestRobot` functionality
is exposed as IPython `%magic` functions...

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

### Variables

Robot Framework uses `${...}` and `@{...}` syntax for accessing variables.
In `%magic` function call parameters
IPython already substitutes Python variables inside `{...}`
with their `str()` conversion.
This conflicts with Robot variable syntax.
To access a Robot variable you need to use double braces:

    %Keyword ${{var}}

Or to expand a list variable:

    %Keyword @{{listvar}}

This way you can also pass Python variables directly to a Robot Keyword.
If the `Robot` can't find the variable in its own dictionary,
lookup is first extended to IPython's `user_ns` (shell level)
and finally to Python's `builtins`.
