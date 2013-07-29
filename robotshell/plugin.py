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

from .magic import RobotMagics, RobotMagic

class RobotPlugin(Plugin):
    def __init__(self, shell):
        Plugin.__init__(self, shell=shell)

        for name, value in os.environ.items():
            self.shell.magics_manager.define_magic(
              '{%s}' % name, lambda magics, _, _value=value: _value)

        self.shell.magics_manager.define_magic(
          'Robot', RobotMagic(robot_plugin=self))

        magics = RobotMagics(robot_plugin=self)
        shell.register_magics(magics)

        self.robot = None
        self.robots = {}
        self.robot_keyword_magics = {}

        # Create initial Test Robot
        self.Robot('Default')

    def Robot(self, name = None):
        if name and (not self.robot or name != self.robot.name):
            try:
                robot = self.robots[name]
            except KeyError:
                robot = TestRobot(name)
                self.robots[name] = robot

            robot_magic = RobotMagic(robot_plugin=self, name=name)
            self.shell.magics_manager.define_magic(
              str(robot_magic), robot_magic)

            for var, value in robot._variables.items():
                self.shell.magics_manager.define_magic(
                  var, lambda self, _, _value=value: _value)

            self.unregister_robot_keyword_magics()
            for lib in robot._libraries:
                self.register_robot_keyword_magics(lib)

            self.shell.prompt_manager.in_template = re.sub(
              r'^(\[Robot.[^\]]+\]\n)?', '[Robot.%s]\n' % name,
              self.shell.prompt_manager.in_template)

            self.robot = robot

        return self.robot

    def Import(self, name):
        library = self.robot.Import(name)
        self.register_robot_keyword_magics(library)
        return library

    def register_robot_keyword_magics(self, library):
        define_magic = self.shell.magics_manager.define_magic

        for keyword in library:
            keywordname = keyword.name.replace(' ', '')
            for name in keywordname, '%s.%s' % (library.name, keywordname):
                def keyword_magic(magics, args, _keyword=keyword):
                    keyword = Keyword(_keyword._handler, self.robot._context)
                    if args:
                        return keyword(*args.split())
                    return keyword()

                keyword_magic.func_name = str(keywordname)
                keyword_magic.__doc__ = keyword.__doc__
                self.robot_keyword_magics[name] = keyword_magic

                define_magic(name, keyword_magic)

    def unregister_robot_keyword_magics(self):
        magics = self.shell.magics_manager.magics['line']
        for name in self.robot_keyword_magics:
            del magics[name]
        self.robot_keyword_magics = {}
