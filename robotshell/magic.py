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
__all__ = ['RobotMagics', 'RobotMagic', 'KeywordMagic', 'KeywordCellMagic']

from IPython.core.magic import Magics, magics_class, line_magic

from .base import ShellBase

@magics_class
class RobotMagics(Magics):
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

class RobotMagicBase(ShellBase):
    def __init__(self, robot_shell):
        ShellBase.__init__(self, robot_shell.shell)
        self.robot_shell = robot_shell

class RobotMagic(RobotMagicBase):
    def __init__(self, name=None, **baseargs):
        RobotMagicBase.__init__(self, **baseargs)
        self.name = name

    @property
    def __doc__(self):
        return self.robot.__doc__

    @property
    def robot(self):
        if self.name:
            return self.robot_shell.robots[self.name]
        return self.robot_shell.robot

    @property
    def magic_name(self):
        robot_magic_name = self.robot_shell.robot_magic_name
        if self.name:
            return '%s.%s' % (robot_magic_name, self.name)
        return robot_magic_name

    def __str__(self):
        return self.magic_name

    def __call__(self, name):
        return self.robot_shell.Robot(self.name or name)

class KeywordMagic(RobotMagicBase):
    def __init__(self, keyword, **baseargs):
        RobotMagicBase.__init__(self, **baseargs)
        self.keyword = keyword

    @property
    def __doc__(self):
        return self.keyword.__doc__

    def __str__(self):
        return self.keyword.name

    def __call__(self, args_str):
        if not args_str:
            args = ()
        elif any(args_str.startswith(c) for c in '[|'):
            args = [s.strip() for s in args_str.strip('[|]').split('|')]
        else:
            args = args_str.split()

        if self.robot_shell.robot_debug_mode:
            return self.keyword.debug(*args)
        return self.keyword(*args)

class KeywordCellMagic(KeywordMagic):
    def __call__(self, args_str):
        args = [s.strip() for s in args_str.strip().split('\n')]
        return self.keyword(*args)
