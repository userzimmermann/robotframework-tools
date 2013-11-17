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

"""robotshell.extension

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Extension']

from robottools import TestRobot

from .magic import RobotMagic


class Extension(TestRobot):
    """Base class for robotshell extensions.

    - Load with ``robotshell.load_robotshell(extensions=[<class>,...]``.
    """
    magic_name = None

    def __init__(self):
        if not self.magic_name:
            self.magic_name = type(self).__name__
        TestRobot.__init__(self, self.magic_name)

    def close(self):
        return None


class ExtensionMagic(RobotMagic):
    def __init__(self, robot, extname=None, **baseargs):
        RobotMagic.__init__(self, robot.magic_name, **baseargs)
        self.extname = extname

    @property
    def magic_name(self):
        magic_name = self.robot.magic_name
        if self.extname:
            return '%s.%s' % (magic_name, self.extname)
        return magic_name

    def __call__(self, args_str):
        if self.extname:
            args_str = self.extname
        extname = self.robot(args_str)
        if extname:
            magic = ExtensionMagic(
              self.robot, extname, robot_shell=self.robot_shell)
            self.line_magics[str(magic)] = magic
        self.robot_shell.Robot(self.robot.magic_name, extname)
