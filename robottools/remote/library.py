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

"""robottools.remote.library

RemoteRobot's library proxy for RobotRemoteServer base.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['RemoteLibrary']

from robottools import TestLibraryInspector


class RemoteLibrary(object):
    """A proxy to :class:`.RemoteRobot`'s imported Test Libraries
       for use with its RobotRemoteServer base,
       which only accepts a single Test Library.

    - Provides a Dynamic Test Library API.
    """
    def __init__(self, robot):
        """Initialize with a :class:`.RemoteRobot` instance.
        """
        self.robot = robot

    def get_keyword_names(self):
        return [keyword.name for lib in self.robot._libraries.values()
                for keyword in TestLibraryInspector(lib)]

    def get_keyword_arguments(self, name):
        keyword = self.robot[name]
        return list(keyword.arguments)

    def get_keyword_documentation(self, name):
        keyword = self.robot[name]
        return keyword.doc

    def run_keyword(self, name, *args, **kwargs):
        keyword = self.robot[name]
        return keyword(*args, **kwargs)

    def __getattr__(self, name):
        """Makes Keywords also directly available as methods.
        """
        try:
            return self.robot[name]
        except KeyError:
            raise AttributeError(name)
