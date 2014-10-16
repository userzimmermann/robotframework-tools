# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2014 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""robottools.utils.normbool

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass, string_types

__all__ = ['normbooltype']

from six.moves import map

from moretools import booltype

from robot.utils import normalize


class Type(type(booltype.base)):
    def __contains__(cls, value):
        return super(Type, cls).__contains__(cls.normalize(value))


class NormalizedBool(with_metaclass(Type, booltype.base)):
    def __init__(self, value):
        try:
            super(NormalizedBool, self).__init__(
              type(self).normalize(value))
        except ValueError as e:
            raise type(e)(repr(value))


def normbooltype(typename='NormalizedBool', true=None, false=None,
                 ignore='', caseless=True, spaceless=True,
                 base=NormalizedBool):

    if not issubclass(base, NormalizedBool):
        raise TypeError("'base' is no subclass of normbooltype.base: %s"
                        % base)

    def normalizer(value):
        if not isinstance(value, string_types):
            return value
        return normalize(value, ignore=normalizer.ignore,
          caseless=normalizer.caseless, spaceless=normalizer.spaceless)

    normalizer.ignore = ignore
    normalizer.caseless = caseless
    normalizer.spaceless = spaceless

    if true:
        true = list(map(normalizer, true))
    if false:
        false = list(map(normalizer, false))

    Bool = booltype(typename, true=true, false=false, base=base)
    type(Bool).normalize = staticmethod(normalizer)
    return Bool


normbooltype.base = NormalizedBool
