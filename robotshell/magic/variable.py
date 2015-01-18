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

"""robotshell.magic.variable

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['VariableMagic']

from .base import RobotMagicBase


class VariableMagic(RobotMagicBase):
    def __init__(self, variable, **baseargs):
        RobotMagicBase.__init__(self, **baseargs)
        self.variable = variable

    def __str__(self):
        #Remove braces from $/@{...} for magic name:
        return self.variable[0] + self.variable[2:-1]

    def __call__(self, args_str):
        if not args_str:
            return self.robot._variables[self.variable]

        args_str = args_str.lstrip('=').lstrip()
        result = self.robot_shell.robot_keyword_magics['RunKeyword'](args_str)
        self.robot._variables[self.variable] = result
        return result
