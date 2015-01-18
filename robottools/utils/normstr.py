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

"""robottools.utils.normbool

normstringclass() creates UserString-derived classes
with normalized data storage and comparisons.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['normstringclass', 'normstringtype']

from six.moves import UserString

from robot.utils import normalize


class NormalizedString(UserString):
    """Base class for :func:`normstringclass` created classes.
    """
    def __init__(self, value):
        """Initialize a NormalizedString instance with a normalized value.
        """
        return UserString.__init__(self, type(self).normalize(value))

    def __cmp__(self, other):
        return cmp(self.data, type(self).normalize(other))

    def __eq__(self, other):
        return (self.data == type(self).normalize(other))

    def __ne__(self, other):
        return (self.data != type(self).normalize(other))

    def __lt__(self, other):
        return (self.data < type(self).normalize(other))

    def __le__(self, other):
        return (self.data <= type(self).normalize(other))

    def __gt__(self, other):
        return (self.data > type(self).normalize(other))

    def __ge__(self, other):
        return (self.data >= type(self).normalize(other))

    def __contains__(self, string):
        return UserString.__contains__(self, type(self).normalize(string))


def normstringclass(typename='NormalizedString', true=None, false=None,
                 ignore='', caseless=True, spaceless=True,
                 base=NormalizedString):

    if not issubclass(base, NormalizedString):
        raise TypeError("'base' is no subclass of normstringclass.base: %s"
                        % base)

    # to be stored as .normalize method of created class
    def normalizer(value):
        """Normalize `value` based on normalizing options
           given to :func:`normstringclass`.
        """
        if isinstance(value, UserString):
            value = value.data
        return normalize(value, ignore=normalizer.ignore,
          caseless=normalizer.caseless, spaceless=normalizer.spaceless)

    # store the normalizing options
    normalizer.ignore = ignore
    normalizer.caseless = caseless
    normalizer.spaceless = spaceless

    class Type(type(base)):
        normalize = staticmethod(normalizer)

    return Type(typename, (base,), {})

normstringtype = normstringclass


normstringclass.base = NormalizedString
