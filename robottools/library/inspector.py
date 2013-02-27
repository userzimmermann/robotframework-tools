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
__all__ = 'TestLibraryInspector', 'MultiTestLibraryInspector',

from collections import OrderedDict
from itertools import chain
from moretools import camelize, decamelize, simpledict

import robot.running

class TestLibraryInspector(object):
  def __init__(self, name):
    self._library = robot.running.TestLibrary(name)

  @property
  def name(self):
    return self._library.name

  def __getitem__(self, name):
    return self._library.get_handler(name)

  def __getattr__(self, name):
    return self._library.get_handler(name)

  def __dir__(self):
    return list(map(camelize, self._library.handlers.keys()))

TestLibrariesDict = simpledict('TestLibrariesDict', dicttype = OrderedDict)

class MultiTestLibraryInspector(object):
  def __init__(self, *libraries):
    libslist = []
    for lib in libraries:
      if type(lib) is not TestLibraryInspector:
        lib = TestLibraryInspector(str(lib))
      libslist.append(lib)
    self.libraries = TestLibrariesDict.frozen(
      (lib.name, lib) for lib in libslist)

  def __getitem__(self, name):
    for libname, lib in self.libraries:
      try:
        return lib[name]
      except KeyError:
        pass
    raise KeyError(name)

  def __getattr__(self, name):
    try:
      return self[name]
    except KeyError:
      raise AttributeError(name)

  def __dir__(self):
    ikeys = chain(*(
      lib._library.handlers.keys() for libname, lib in self.libraries))
    return list(map(camelize, ikeys))
