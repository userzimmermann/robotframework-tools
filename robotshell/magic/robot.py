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

"""robotshell.magic.robot

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['RobotMagic']

from .base import RobotMagicBase


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
