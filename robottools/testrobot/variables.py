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
__all__ = ['variablesclass']

import sys

from robot.errors import DataError


def variablesclass(base, extra_getters=None):
    """Creates custom Variables wrapper classes
       with support for ``extra_getters`` (extra lookup sources),
       which should work like dicts and support ``$/@/&{...}`` style keys.
    """
    class Variables(base):
        """Base class for creating custom Variables wrapper classes
           via :func:`robottools.testrobot.variables.variablesclass`
           with support for ``extra_getters`` (extra lookup sources).
        """
        _extra_getters = extra_getters or ()

        def __getitem__(self, key):
            """Also looks up ``self._extra_getters``.
            """
            try:
                return base.__getitem__(self, key)
            except DataError:
                if self._extra_getters:
                    for getter in self._extra_getters:
                        try:
                            return getter(key)
                        except (LookupError, DataError):
                            pass
                raise

        if not issubclass(base, object):
            #==> PY2 old style base class from Robot 2.8
            #==> __getattribute__ below not used
            @property
            def current(self):
                return self

        def __getattribute__(self, name):
            """Makes sure that ``self.current`` is handled correctly
               according to the Variables wrapping approach.
            """
            try:
                value = base.__getattribute__(self, name)
            except AttributeError:
                # Robot 2.8: just return self as `current`
                if name == 'current':
                    return self
                raise
            # Robot 2.9: wrap `current`'s class with same options
            if (name == 'current'
                # (if not done yet)
                and type(value).__module__ != __name__
                ):
                value.__class__ = variablesclass(value.__class__,
                  extra_getters=self._extra_getters)
            return value

        _parents = []

    return Variables
