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

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestRobot']

from moretools import isidentifier

from robot.errors import DataError
from robot.conf import RobotSettings
from robot.variables import GLOBAL_VARIABLES, init_global_variables

from robottools.library.inspector import TestLibraryInspector

init_global_variables(RobotSettings())

class TestRobot(object):
    def __init__(self, name):
        self.name = name
        self._variables = GLOBAL_VARIABLES.copy()
        self._libraries = []

    @property
    def __doc__(self):
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Import] ' + lib.name for lib in self._libraries)))

    def Import(self, lib):
        if type(lib) is not TestLibraryInspector:
            lib = TestLibraryInspector(lib)
        self._libraries.append(lib)
        return lib

    def __getitem__(self, name):
        if name.startswith('$'):
            try:
                return self._variables[name]
            except DataError as e:
                raise KeyError(str(e))
        for lib in self._libraries:
            if lib.name == name:
                return lib
            try:
                return lib[name]
            except KeyError as e:
                pass
        raise e

    def __getattr__(self, name):
        if name.isupper(): # Use as variable name
            name = '${%s}' % name
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(str(e))

    def __dir__(self):
        names = []
        for name in self._variables:
            name = name[2:-1] # Strip ${}
            if isidentifier(name):
                names.append(name.upper())
        for lib in self._libraries:
            names.append(lib.name)
            # dir() returns the Library's CamelCase Keyword names
            names.extend(dir(lib))
        return names

    def __str__(self):
        return self.name

    def __repr__(self):
        return '[Robot] %s' % self
