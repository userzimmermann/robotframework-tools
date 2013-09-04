Robot Framework Tools
=====================

The ``robotframework-tools`` provide:

- A simple framework for creating Dynamic Test Libraries.
- Tools for inspecting Test Libraries and running interactive Robot sessions.
- An interactive Robot shell extension for IPython.

1. Creating Dynamic Test Libraries
----------------------------------

::
  from robottools import testlibrary

  TestLibrary = testlibrary()

Defined in a module also called ``TestLibrary``,
this generated Dynamic ``TestLibrary`` type
could now directly be imported in Robot Framework.
It features all the required methods:

- ``get_keyword_names``
- ``get_keyword_arguments``
- ``run_keyword``

But the ``TestLibrary`` has no Keywords so far...
To add some just use the ``TestLibrary.keyword`` decorator::

  def no_keyword(...):
      ...

  @TestLibrary.keyword
  def some_keyword(self, arg, *rest):
      ...

A keyword function can be defined anywhere in any scope.
The ``TestLibrary.keyword`` decorator
always links it to the ``TestLibrary``.
And when called as a Keyword from Robot Framework
the ``self`` parameter will always get the ``TestLibrary`` instance.

You may want to define your keyword methods
at your Test Library class scope.
Just derive your actual Dynamic Test Library class from ``TestLibrary``::

  class RealLibrary(TestLibrary):
      def no_keyword(self, ...):
          pass

      @TestLibrary.keyword
      def some_other_keyword(self, arg, *rest):
          ...
          self.no_keyword(...)
          ...
