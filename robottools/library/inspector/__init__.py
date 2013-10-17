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

"""robottools.library.inspector

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = [
  'ROBOT_LIBRARIES',
  'TestLibraryImportError', 'TestLibraryInspector',
  # From .multi:
  'MultiTestLibraryInspector',
  ]

from moretools import camelize

from path import path as Path

import robot.errors
import robot.running
import robot.running.baselibrary
import robot.libraries

from .keyword import KeywordInspector


ROBOT_LIBRARIES_PATH = Path(robot.libraries.__file__).dirname()
ROBOT_LIBRARIES = set()
for path in ROBOT_LIBRARIES_PATH.walkfiles():
    name = str(path.basename().splitext()[0])
    if name[0].isupper():
        ROBOT_LIBRARIES.add(name)
del path, name

ROBOT_LIBRARIES = sorted(ROBOT_LIBRARIES)


class TestLibraryImportError(ImportError):
  pass


class TestLibraryInspectorMeta(type):
    def __getattr__(self, libname):
        try:
            return TestLibraryInspector(libname)
        except TestLibraryImportError as e:
            raise AttributeError(str(e))

    def __dir__(self):
        return list(ROBOT_LIBRARIES)


class TestLibraryInspector(object):
    __metaclass__ = TestLibraryInspectorMeta

    def __init__(self, lib):
        if isinstance(lib, robot.running.baselibrary.BaseLibrary):
            self._library = lib
            return
        try:
            self._library = robot.running.TestLibrary(lib)
        except robot.errors.DataError as e:
            raise TestLibraryImportError(str(e))

    @property
    def __doc__(self):
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Keyword] %s [%s]' % (keyword.name, keyword.arguments)
          for keyword in self)))

    @property
    def name(self):
        return self._library.name

    def __iter__(self):
        for keyword in self._library.handlers.values():
            yield KeywordInspector(keyword)

    def __getitem__(self, name):
        try:
            handler = self._library.get_handler(name)
        except robot.errors.DataError as e:
            raise KeyError(str(e))
        return KeywordInspector(handler)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(str(e))

    def __dir__(self):
        return list(map(camelize, self._library.handlers.keys()))

    def __str__(self):
        return self._library.name

    def __repr__(self):
        return '[Library] %s' % self


from .multi import MultiTestLibraryInspector
