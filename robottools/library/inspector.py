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
__all__ = (
  'ROBOT_LIBRARIES',
  'TestLibraryImportError',
  'TestLibraryInspector', 'MultiTestLibraryInspector',
  )

from collections import OrderedDict
from itertools import chain
from moretools import camelize, decamelize, simpledict

from path import path as Path

import robot.errors
import robot.running
import robot.running.baselibrary
import robot.libraries

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

class KeywordArgumentsInspector(object):
    def __init__(self, arguments):
        self._arguments = arguments

    def __getattr__(self, name):
        return getattr(self._arguments, name)

    def __dir__(self):
        return ['positional', 'defaults', 'varargs', 'kwargs']

    def __iter__(self):
        args = self._arguments
        for argname, defaults_index in zip(
          args.positional, range(-len(args.positional), 0)
          ):
            try:
                default = args.defaults[defaults_index]
            except IndexError:
                yield argname
            else:
                yield '%s=%s' % (argname, default)
        if args.varargs:
            yield '*' + args.varargs
        if args.kwargs:
            yield '**' + args.kwargs

    def __str__(self):
        return ' | '.join(self)

    def __repr__(self):
        return '[Arguments] %s' % self

class KeywordInspector(object):
    def __init__(self, handler):
        self._handler = handler

    @property
    def __doc__(self):
        return "%s\n\n%s" % (repr(self), self._handler.doc)

    @property
    def arguments(self):
        return KeywordArgumentsInspector(self._handler.arguments)

    def __getattr__(self, name):
        return getattr(self._handler, name)

    def __dir__(self):
        return ['name', 'doc', 'shortdoc']

    def __str__(self):
        return self._handler.longname

    def __repr__(self):
        return '[Keyword] %s [ %s ]' % (self, self.arguments)

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

TestLibrariesDict = simpledict('TestLibrariesDict', dicttype=OrderedDict)

class MultiTestLibraryInspector(object):
    def __init__(self, *libraries):
        libslist = []
        for lib in libraries:
            if type(lib) is not TestLibraryInspector:
                lib = TestLibraryInspector(str(lib))
            libslist.append(lib)
        self.libraries = TestLibrariesDict.frozen(
          (lib.name, lib) for lib in libslist)

    @property
    def __doc__(self):
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Keyword] %s [%s]' % (keyword.name, keyword.arguments)
          for keyword in self)))

    def __iter__(self):
        for libname, lib in self.libraries:
            for keyword in lib._library.handlers.values():
                yield KeywordInspector(keyword)

    def __getitem__(self, name):
        for libname, lib in self.libraries:
            try:
                return lib[name]
            except KeyError as e:
                pass
        raise e

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(str(e))

    def __dir__(self):
        ikeys = chain(*(
          lib._library.handlers.keys() for libname, lib in self.libraries))
        return list(map(camelize, ikeys))

    def __str__(self):
        return ' '.join(sorted(
          item[0] for item in self.libraries))

    def __repr__(self):
        return '[Libraries] %s' %self
