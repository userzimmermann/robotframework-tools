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

"""robotshell.base

ShellBase class for IPython extensions with common shell access helpers.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['ShellBase']


class ShellBase(object):
    """Helper base class for IPython extension classes.
    """
    def __init__(self, shell):
        """Initialize with IPython `shell` instance,
           as passed from IPython to load_ipython_extension().
        """
        self.shell = shell

    @property
    def line_magics(self):
        """IPython's dict of registered line magic functions.
        """
        return self.shell.magics_manager.magics['line']

    @property
    def cell_magics(self):
        """IPython's dict of registered cell magic functions.
        """
        return self.shell.magics_manager.magics['cell']

    @property
    def in_template(self):
        """IPython's current input prompt template.
        """
        return self.shell.prompt_manager.in_template

    @in_template.setter
    def in_template(self, value):
        """Change IPython's current input prompt template to `value`.
        """
        self.shell.prompt_manager.in_template = value
