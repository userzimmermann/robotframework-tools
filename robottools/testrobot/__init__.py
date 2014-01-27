# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013 Stefan Zimmermann <zimmermann.code@gmail.com>
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

- Provides the interactive TestRobot interface.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestRobot']

import sys
import warnings
import logging

from moretools import isidentifier

from robot.errors import DataError
from robot.model import TestSuite
from robot.conf import RobotSettings
from robot.variables import GLOBAL_VARIABLES, init_global_variables
from robot.running.namespace import Namespace

from robottools import TestLibraryInspector

from .variables import variablesclass
from .output import Output
from .context import Context
from .library import TestLibrary
from .keyword import Keyword


class TestRobot(object):
    """An interactive Robot Framework interface.
    """
    def __init__(self, name, variable_getters=None):
        """Initialize with a `name`
           and optional additional variable lookup functions.

        - If a Variable is not found in the Robot's Variables dictionary,
          the `variable_getters` will be called in the given order
          with the Variable string in Robot syntax ($/@{...})
          until no `LookupError` or `DataError` is raised.
          (Used by the `robot_shell` to extend Variables lookup
           to IPython's `user_ns` and Python's `builtins`).

        :param variable_getters: A sequence of callables.
        """
        self.name = name
        if not GLOBAL_VARIABLES: #HACK
            init_global_variables(RobotSettings())
        self._variables = GLOBAL_VARIABLES.copy()
        #HACK even more to extend variable lookup:
        self._variables.__class__ = variablesclass(
          extra_getters=variable_getters)
        self._output = Output()
        self._context = Context(testrobot=self)
        self._suite = TestSuite(name)
        self._namespace = Namespace(
          self._suite, self._variables, None, [], None)
        self._libraries = {}

        self.Import('BuiltIn')

    @property
    def __doc__(self):
        """Dynamic doc string listing imported Test Libraries.
        """
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Import] ' + lib.name
          for alias, lib in self._libraries.items())))

    def Import(self, lib, alias=None):
        """Import a Test Library with an optional `alias` name.
        """
        if type(lib) is not TestLibraryInspector:
            #HACK: `with` registers Output to LOGGER
            with self._output:
                lib = TestLibraryInspector(lib)
        self._libraries[alias or lib.name] = lib
        return TestLibrary(lib._library, self._context)

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
            if alias == name:
                return TestLibrary(lib._library, self._context)
            try:
                keyword = lib[name]
            except KeyError:
                pass
            else:
                return Keyword(keyword._handler, self._context)
        raise KeyError(name)

    def __getattr__(self, name):
        """Get Robot Variables, Test Libraries and Keywords by name.

        - Keyword names can be in any case (lower_case, CamelCase, ...).
        """
        try:
            return self[name]
        except KeyError as e:
            try:
                return self._variables['${%s}' % name]
            except DataError:
                raise AttributeError(str(e))

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
            # dir() returns the Library's CamelCase Keyword names
            names.extend(dir(lib))
        return names

    def __str__(self):
        return self.name

    def __repr__(self):
        return '[Robot] %s' % self
