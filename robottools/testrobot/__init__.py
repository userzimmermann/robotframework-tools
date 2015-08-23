# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# robotframework-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# robotframework-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with robotframework-tools. If not, see <http://www.gnu.org/licenses/>.

"""robottools.testrobot

Provides the interactive TestRobot interface.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import reraise

__all__ = ['TestRobot',
  'TestResult', # from .result
  ]

from inspect import getargspec
from functools import partial

from moretools import isidentifier

from robot.errors import DataError
from robot.model import TestSuite
from robot.conf import RobotSettings
try:
    from robot.variables import GLOBAL_VARIABLES, init_global_variables
except ImportError: # Robot 2.9
    from robot.variables import VariableScopes
from robot.running.namespace import Namespace
from robot.running.runner import Runner
from robot.running import TestSuiteBuilder

from robottools import TestLibraryInspector

from .variables import variablesclass
from .output import Output
from .context import Context
from .library import TestLibrary
from .keyword import Keyword
from .result import TestResult


class TestRobot(object):
    """An interactive Robot Framework interface.
    """
    def __init__(self, name, BuiltIn=True, variable_getters=None):
        """Initialize with a `name`
           and optional additional variable lookup functions.

        - If a Variable is not found in the Robot's Variables dictionary,
          the `variable_getters` will be called in the given order
          with the Variable string in Robot syntax ($/@{...})
          until no `LookupError` or `DataError` is raised.
          (Used by the `robot_shell` to extend Variables lookup
           to IPython's `user_ns` and Python's `builtins`).

        :param BuiltIn: Import RFW's BuiltIn Library by default?
        :param variable_getters: A sequence of callables.
        """
        self.name = name
        self.debug = False
        try:
            GLOBAL_VARIABLES
        except NameError: # Robot 2.9
            self._variables = VariableScopes(RobotSettings())
        else:
            if not GLOBAL_VARIABLES: #HACK
                init_global_variables(RobotSettings())
            self._variables = GLOBAL_VARIABLES.copy()
        #HACK even more to extend variable lookup:
        self._variables.__class__ = variablesclass(
          self._variables.__class__, extra_getters=variable_getters)
        self._output = Output()
        self._context = Context(testrobot=self)
        self._suite = TestSuite(name)
        namespace = partial(Namespace,
          suite=self._suite, variables=self._variables,
          user_keywords=[], imports=None)
        if 'parent_variables' in getargspec(Namespace.__init__).args:
            self._namespace = namespace(parent_variables=None)
        else: # Robot 2.9
            self._namespace = namespace()

        if BuiltIn:
            self.Import('BuiltIn')

    @property
    def _libraries(self):
        """Get the TestRobot's internal RFW library dict
           (values not wrapped with :class:`robottools.TestLibraryInspector`
            or :class:`robottools.testrobot.TestLibrary`).
        """
        try:
            return self._namespace._testlibs
        except AttributeError: # Robot 2.9
            return self._namespace._kw_store.libraries

    @property
    def __doc__(self):
        """Dynamic doc string, listing imported Test Libraries.
        """
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Import] ' + lib.name
          for alias, lib in self._libraries.items())))

    def Import(self, lib, args=None, alias=None):
        """Import a Test Library with an optional `alias` name.
        """
        if not isinstance(lib, TestLibraryInspector):
            #HACK: `with` adds Context to robot.running.EXECUTION_CONTEXTS
            # and registers Output to robot.output.LOGGER
            with self._context:
                lib = self._context.importer.import_library(lib,
                  args and list(args), alias, None)
                self._libraries[alias or lib.name] = lib
                lib = TestLibraryInspector(lib)
                ## lib = TestLibraryInspector(lib, *(args or ()))
        # Put lib in testrobot's TestLibrary wrapper
        #  for calling Keywords with TestRobot's context:
        return TestLibrary(lib._library, context=self._context)

    def Run(self, path, **options):
        debug = options.pop('debug', self.debug)
        # post processed options
        settings = RobotSettings(**options)
        builder = TestSuiteBuilder()
        suite = builder.build(path)
        with self._context:
            runner = Runner(self._output, settings)
            suite.visit(runner)
            result = runner.result
            if debug and result.return_code:
                reraise(*self._output._last_fail_exc)
            return TestResult(runner.result, **options)

    def __getitem__(self, name):
        """Get variables (with $/@{...} syntax),
           Test Libraries and Keywords by name.

        - Keyword names can be in any case (like in a Test Script).
        """
        if any(name.startswith(c) for c in '$@'):
            try:
                return self._variables[name]
            except DataError as e:
                raise KeyError(str(e))
        for alias, lib in self._libraries.items():
            # Put lib in testrobot's TestLibrary wrapper
            #  for calling Keywords with TestRobot's context:
            lib = TestLibrary(lib, context=self._context)
            if alias == name:
                return lib
            try:
                keyword = lib[name]
            except KeyError:
                pass
            else:
                keyword = Keyword(keyword._handler, context=self._context)
                if self.debug:
                    return keyword.debug
                return keyword
        raise KeyError("No Test Library or Keyword named '%s'." % name)

    def __getattr__(self, name):
        """Get Robot Variables, Test Libraries and Keywords by name.

        - Keyword names can be in any case (lower_case, CamelCase, ...),
          but CamelCase is the preferred style.
        """
        try: # Delegate to self.__getitem__:
            return self[name]
        except KeyError:
            try:
                return self._variables['${%s}' % name]
            except DataError:
                raise AttributeError(
                  "No Test Library, Keyword or Variable named '%s'."
                  % name)

    def __dir__(self):
        """List all Robot Variables (UPPER_CASE),
           Test Libraries and Keyword (CamelCase) names,
           which are valid Python identifiers.
        """
        names = []
        for name in self._variables:
            name = name[2:-1] # Strip ${}
            if isidentifier(name):
                names.append(name.upper())
        for alias, lib in self._libraries.items():
            names.append(alias)
            # dir() returns the Library's CamelCase Keyword names:
            names.extend(dir(lib))
        return names

    def __str__(self):
        return self.name

    def __repr__(self):
        return '[Robot] %s' % self
