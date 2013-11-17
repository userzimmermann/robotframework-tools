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

"""robottools.testrobot

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['VariablesBase', 'variablesclass']

from robot.errors import DataError
import robot.variables


class VariablesBase(robot.variables.Variables):
    def __getitem__(self, key):
        try:
            return robot.variables.Variables.__getitem__(self, key)
        except DataError:
            for getter in self._extra_getters:
                try:
                    return getter(key)
                except (KeyError, DataError):
                    pass
        raise DataError(key)


def variablesclass(extra_getters=None):
    return type(VariablesBase)('Variables', (VariablesBase,), {
      '_extra_getters': extra_getters or (),
      })
