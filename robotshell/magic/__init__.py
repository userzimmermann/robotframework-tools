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

"""robotshell.magic

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = [
  'RobotMagics', 'RobotMagic', 'KeywordMagic', 'KeywordCellMagic',
  'VariableMagic']

from IPython.core.magic import Magics, magics_class, line_magic

from robottools.testrobot.output import LOG_LEVELS

from .robot import RobotMagic
from .keyword import KeywordMagic, KeywordCellMagic
from .variable import VariableMagic


class RobotMagicsMeta(type(Magics)):
    def __new__(mcs, name, bases, attrs):
        for level in LOG_LEVELS:

            def LEVEL(self, _, _level=level):
                self.robot_shell.robot._output.set_log_level(_level)

            LEVEL.__name__ = level
            attrs[level] = line_magic(LEVEL)

        return type(Magics).__new__(mcs, name, bases, attrs)


@magics_class
class RobotMagics(Magics):
    __metaclass__ = RobotMagicsMeta

    def __init__(self, robot_shell):
        Magics.__init__(self, robot_shell.shell)
        self.robot_shell = robot_shell

    def robot_mode_magic(func):
        def magic(self, mode):
            attrname = func.func_name + '_mode'
            title = attrname.capitalize().replace('_', ' ')

            current = getattr(self.robot_shell, attrname)
            if not mode:
                value = not current
            else:
                mode = mode.lower()
                if mode in ['on', 'yes', 'true', '1']:
                    value = True
                elif mode.lower() in ['off', 'no', 'false', '0']:
                    value = True
                else:
                    raise ValueError(mode)
            setattr(self.robot_shell, attrname, value)
            print("%s is: %s" % (title, value and "ON" or "OFF"))

            func(self, mode)

        magic.func_name = func.func_name
        return magic

    @line_magic
    @robot_mode_magic
    def robot_debug(self, mode=None):
        pass

    @line_magic
    @robot_mode_magic
    def robot_cell_magic(self, mode=None):
        pass

    @line_magic
    def Import(self, libname_as_alias):
        try:
            libname, _as_, alias = libname_as_alias.split()
            if _as_ != 'as':
                raise ValueError
        except ValueError:
            libname = libname_as_alias
            alias = None
        return self.robot_shell.Import(libname, alias)

    @line_magic
    def Close(self, _):
        self.robot_shell.Close()
