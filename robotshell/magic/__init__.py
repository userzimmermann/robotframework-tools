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

"""robotshell.magic

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass

__all__ = [
  'RobotMagics', 'RobotMagicBase', 'RobotMagic',
  'KeywordMagic', 'KeywordCellMagic',
  'VariableMagic']

import sys

from IPython.core.magic import Magics, magics_class, line_magic

from robottools.testrobot.output import LOG_LEVELS

from .base import RobotMagicBase
from .robot import RobotMagic
from .keyword import KeywordMagic, KeywordCellMagic
from .variable import VariableMagic


# on import robot, robot.run module gets overwritten
# with robot.run.run() function
RFW = sys.modules['robot.run'].RobotFramework()


class RobotMagicsMeta(type(Magics)):
    def __new__(mcs, name, bases, attrs):
        for level in LOG_LEVELS:

            def LEVEL(self, _, _level=level):
                self.robot_shell.robot._output.set_log_level(_level)

            LEVEL.__name__ = level
            attrs[level] = line_magic(LEVEL)

        return type(Magics).__new__(mcs, name, bases, attrs)


@magics_class
class RobotMagics(with_metaclass(RobotMagicsMeta, Magics)):
    def __init__(self, robot_shell):
        Magics.__init__(self, robot_shell.shell)
        self.robot_shell = robot_shell

    def robot_mode_magic(func):
        def magic(self, mode):
            attrname = func.__name__ + '_mode'
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

        magic.__name__ = func.__name__
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
    def Import(self, libname_and_args_as_alias):
        try:
            libname_and_args, _as_, alias = (
              libname_and_args_as_alias.rsplit(None, 2))
            if _as_ != 'AS':
                raise ValueError
        except ValueError:
            libname_and_args = libname_and_args_as_alias
            alias = None
        try:
            libname, args = libname_and_args.split(None, 1)
            args = args.split()
        except ValueError:
            libname = libname_and_args
            args = None
        return self.robot_shell.Import(libname, args, alias=alias)

    @line_magic
    def Run(self, options_and_path):
        options, sources = RFW.parse_arguments(
          str(options_and_path).split())
        return self.robot_shell.Run(*sources, **options)

    @line_magic
    def Close(self, _):
        self.robot_shell.Close()
