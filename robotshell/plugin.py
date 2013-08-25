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

"""robotshell.plugin

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['RobotPlugin']

import re
import os

from IPython.core.plugin import Plugin

from robottools import TestRobot
from robottools.testrobot import Keyword

from .magic import RobotMagics, RobotMagic, KeywordMagic, KeywordCellMagic

class RobotPlugin(Plugin):
    # To support customization in derived Plugins
    robot_magic_name = 'Robot'

    robot_debug_mode = False
    robot_cell_magic_mode = False

    def __init__(self, shell, default_robot_name='Default'):
        Plugin.__init__(self, shell=shell)

        for name, value in os.environ.items():
            self.shell.magics_manager.define_magic(
              '{%s}' % name, lambda magics, _, _value=value: _value)

        self.shell.magics_manager.define_magic(
          self.robot_magic_name, RobotMagic(robot_plugin=self))

        magics = RobotMagics(robot_plugin=self)
        shell.register_magics(magics)

        self.robot = None
        self.robots = {}
        self.robot_keyword_magics = {}
        self.robot_keyword_cell_magics = {}

        # Create initial default Test Robot
        self.Robot(default_robot_name)

    def Robot(self, name = None):
        if name and (not self.robot or name != self.robot.name):
            try:
                robot = self.robots[name]
            except KeyError:
                robot = TestRobot(name)
                self.robots[name] = robot
            self.robot = robot

            robot_magic = RobotMagic(name, robot_plugin=self)
            self.shell.magics_manager.define_magic(
              str(robot_magic), robot_magic)

            for var, value in robot._variables.items():
                self.shell.magics_manager.define_magic(
                  var, lambda self, _, _value=value: _value)

            self.unregister_robot_keyword_magics()
            for alias, lib in robot._libraries.items():
                self.register_robot_keyword_magics(alias, lib)

            self.shell.prompt_manager.in_template = re.sub(
              r'^(\[%s.[^\]]+\]\n)?' % self.robot_magic_name,
              '[%s.%s]\n' % (self.robot_magic_name, name),
              self.shell.prompt_manager.in_template)

        return self.robot

    def Import(self, libname, alias=None):
        library = self.robot.Import(libname, alias)
        self.register_robot_keyword_magics(alias or libname, library)
        return library

    def register_robot_keyword_magics(self, libalias, library):
        define_magic = self.shell.magics_manager.define_magic
        cell_magics = self.shell.magics_manager.magics['cell']

        for keyword in library:
            keywordname = keyword.name.replace(' ', '')
            for name in keywordname, '%s.%s' % (libalias, keywordname):
                keyword = Keyword(keyword._handler, self.robot._context)

                keyword_magic = KeywordMagic(keyword, robot_plugin=self)
                self.robot_keyword_magics[name] = keyword_magic

                define_magic(name, keyword_magic)

                ## keyword_cell_magic = KeywordCellMagic(
                ##   keyword, robot_plugin=self)
                ## self.robot_keyword_cell_magics[name] = keyword_cell_magic

                ## cell_magics[name] = keyword_cell_magic

    def unregister_robot_keyword_magics(self):
        magics = self.shell.magics_manager.magics['line']
        for name in self.robot_keyword_magics:
            del magics[name]
        self.robot_keyword_magics = {}

        magics = self.shell.magics_manager.magics['cell']
        for name in self.robot_keyword_cell_magics:
            del magics[name]
        self.robot_keyword_cell_magics = {}
