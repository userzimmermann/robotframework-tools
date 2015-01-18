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

"""robottools.library.inspector.multi

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['MultiTestLibraryInspector']

from collections import OrderedDict
from itertools import chain
from moretools import camelize, simpledict

from . import TestLibraryInspector
from .keyword import KeywordInspector


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
        return ' '.join(sorted(libname for libname, lib in self.libraries))

    def __repr__(self):
        return '[Libraries] %s' % self
