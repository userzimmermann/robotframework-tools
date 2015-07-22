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

"""robottools.testrobot.variables

Wrapping Robot Framework's Variables for use with TestRobot.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['VariablesBase', 'variablesclass']

from robot.errors import DataError
try: # Robot 2.9
    from robot.variables import VariableScopes
    Variables = VariableScopes
except ImportError:
    VariableScopes = None
    from robot.variables import Variables


class VariablesBase(Variables):
    """Base class for creating custom Variables wrapper classes
       via :func:`robottools.testrobot.variables.variablesclass`
       with support for ``extra_getters`` (extra lookup sources).
    """
    def __getitem__(self, key):
        try:
            return Variables.__getitem__(self, key)
        except DataError:
            for getter in self._extra_getters:
                try:
                    return getter(key)
                except (LookupError, DataError):
                    pass
        raise DataError(key)

    if not VariableScopes: # Robot 2.8
        @property
        def current(self):
            return self

    _parents = []


def variablesclass(extra_getters=None):
    """Creates custom Variables wrapper classes
       with support for ``extra_getters`` (extra lookup sources),
       which should work like dicts and support ``$/@/&{...}`` style keys.
    """
    return type(VariablesBase)('Variables', (VariablesBase,), {
      '_extra_getters': extra_getters or (),
      })
