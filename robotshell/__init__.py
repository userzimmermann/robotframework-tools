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

"""robotshell

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['RobotMagicBase', 'Extension', 'load_robotshell']

from robottools import __version__, __requires__, __extras__

__requires__ += __extras__['robotshell'].checked
del __extras__


from .shell import RobotShell
from .magic import RobotMagicBase
from .extension import Extension


robot_shell = None


def load_ipython_extension(shell):
    global robot_shell
    if robot_shell:
        return
    robot_shell = RobotShell(shell)


def load_robotshell(shell, extensions=[]):
    load_ipython_extension(shell)
    for extcls in extensions:
        robot_shell.register_extension(extcls)
