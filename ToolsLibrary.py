# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
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

"""ToolsLibrary

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['ToolsLibrary', 'register_bool_class', 'register_bool_type']

from robottools import __version__, __requires__

from moretools import boolclass, isboolclass, isstring

import robot.running
from robot.running.namespace import IMPORTER
from robot.parsing.settings import Library as LibrarySetting
from robot.utils import NormalizedDict, normalize

from robot.libraries.BuiltIn import BuiltIn

from robottools import testlibrary, normboolclass, RobotBool


BUILTIN = BuiltIn()


TestLibrary = testlibrary()
keyword = TestLibrary.keyword


class ToolsLibrary(TestLibrary):

    ROBOT_LIBRARY_VERSION = __version__

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    @keyword
    def reload_library(self, name, *args):
        """Reload an already imported Test Library
           with given `name` and optional `args`.

        This also leads to a reload of the Test Library Keywords,
        which allows Test Libraries to dynamically extend or change them.
        """
        #HACK
        namespace = BUILTIN._namespace
        try:
            libs = namespace._testlibs
        except AttributeError: # Robot 2.9
            libs = namespace._kw_store.libraries
        cache = IMPORTER._library_cache
        setting = LibrarySetting(None, name, args)
        libargs = setting.args
        alias = setting.alias
        if (alias or name) not in libs:
            raise RuntimeError(
              "Test Library '%s' was not imported yet." % name)
        del libs[name]
        #HACK even worse :)
        cache = IMPORTER._library_cache
        lib = robot.running.TestLibrary(name, libargs)
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

    @keyword.normalized_kwargs
    def convert_to_bool(self, value, *true_false, **options):
        if true_false:
            lists = NormalizedDict({'true': [], 'false': []})
            # choose the first list to fill with items
            #  based on given TRUE or FALSE specifier:
            try:
                t_or_f_list = lists[true_false[0]]
            except KeyError:
                raise ValueError("Expected TRUE or FALSE, not: %s"
                                 % repr(true_false[0]))
            for item in true_false[1:]:
                if item in lists: #==> is new TRUE or FALSE specifier
                    #==> switch to corresponding list
                    t_or_f_list = lists[item]
                    if t_or_f_list:
                        raise ValueError("Multiple %s lists specfied."
                                         % normalize(item).upper())
                else:
                    t_or_f_list.append(item)
            for key, items in lists.items():
                if not items:
                    raise ValueError("No %s list specified." % key.upper())
            if RobotBool(options.get('normalized', True)):
                boolcls = normboolclass(**lists)
            else:
                boolcls = boolclass(**lists)
        else:
            boolcls = options.get('boolclass') or options.get('booltype')
            if not boolcls: # fallback to robot's default bool conversion
                return BUILTIN.convert_to_boolean(value)

            if isstring(boolcls):
                try: # is a registered bool class name?
                    boolcls = BOOL_CLASSES[boolcls]
                except KeyError:
                    if '.' not in boolcls:
                        raise ValueError(
                          "No such bool class registered: '%s'" % boolcls)
                    modname, clsname = boolcls.rsplit('.', 1)
                    try: # is an importable 'module.class' string?
                        boolcls = getattr(__import__(modname), clsname)
                    except (ImportError, AttributeError):
                        raise ValueError(
                          "Can't import bool class: '%s'" % boolcls)
            elif not isboolclass(boolcls):
                raise TypeError("No bool class: %s" % repr(boolcls))

        BUILTIN._log_types(value)
        return boolcls(value)


BOOL_CLASSES = BOOL_TYPES = {}


def register_bool_class(cls_or_name, name=None,
  true=None, false=None, ignore=None, caseless=True, spaceless=True
  ):
    if isstring(cls_or_name):
        name = cls_or_name
        Bool = normboolclass(name, true=true, false=false,
          ignore=ignore, caseless=caseless, spaceless=spaceless)
    else:
        if not isboolclass(cls_or_name):
            raise TypeError("No bool class: %s" % repr(cls_or_name))
        Bool = cls_or_name
        if not name:
            name = Bool.__name__
    BOOL_CLASSES[name] = Bool

register_bool_type = register_bool_class
