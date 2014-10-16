# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2014 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""ToolsLibrary

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import string_types

__all__ = ['ToolsLibrary']

from moretools import isbooltype

import robot.running
from robot.running.namespace import IMPORTER

from BuiltIn import BuiltIn

from robottools import testlibrary, normbooltype


BUILTIN = BuiltIn()


TestLibrary = testlibrary()
keyword = TestLibrary.keyword


class ToolsLibrary(TestLibrary):

    @keyword
    def reload_library(self, name, *args):
        """Reload an already imported Test Library
           with given `name` and optional `args`.

        This also leads to a reload of the Test Library Keywords,
        which allows Test Libraries to dynamically extend or change them.
        """
        #HACK
        libs = BUILTIN._namespace._testlibs
        if name not in libs:
            raise RuntimeError(
              "Test Library '%s' was not imported yet." % name)
        del libs[name]
        #HACK even worse :)
        cache = IMPORTER._library_cache
        lib = robot.running.TestLibrary(name, args)
        key = (name, lib.positional_args, lib.named_args)
        key = cache._norm_path_key(key)
        try:
            index = cache._keys.index(key)
        except ValueError:
            pass
        else:
            cache._keys.pop(index)
            cache._items.pop(index)

        BUILTIN.import_library(name, *args)

    @keyword
    def convert_to_bool(self, value, bool_type=bool):
        if isinstance(bool_type, string_types):
            try:
                bool_type = BOOL_TYPES[bool_type]
            except KeyError:
                raise ValueError("No such bool type registered: '%s'"
                                 % bool_type)
        elif not isbooltype(bool_type):
            raise TypeError("No bool type: %s" % repr(bool_type))
        return bool_type(value)


BOOL_TYPES = {}


def register_bool_type(cls_or_name, name=None,
  true=None, false=None, ignore=None, caseless=True, spaceless=True
  ):
    if isinstance(cls_or_name, string_types):
        name = cls_or_name
        Bool = normbooltype(name, true=true, false=false,
          ignore=ignore, caseless=caseless, spaceless=spaceless)
    else:
        if not isbooltype(cls_or_name):
            raise TypeError("No bool type: %s" % repr(cls_or_name))
        Bool = cls_or_name
        if not name:
            name = Bool.__name__
    BOOL_TYPES[name] = Bool
