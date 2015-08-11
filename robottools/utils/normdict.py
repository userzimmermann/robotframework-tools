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

"""robottools.utils.normdict

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['NormalizedDict', 'normdictclass', 'normdicttype']

from six import iterkeys, iteritems
from six.moves import UserString, UserDict

from robot.utils import normalize, NormalizedDict as base


# check for Robot 2.8
_has_UserDict_base = issubclass(base, UserDict)


class NormalizedDict(base):

    @property
    def meta(self):
        return type(self)

    #HACK: internally used by robot.utils.NormalizedDict base
    # (normally dynamically created and assigned in base __init__)
    @property
    def _normalize(self):
        return self.__dict__.get('_normalize') or type(self).normalize

    #HACK: only let robot.utils.NormalizedDict change
    # the internal _normalize function if no .meta.normalize is defined
    @_normalize.setter
    def _normalize(self, func):
        if not hasattr(type(self), 'normalize'):
            self.__dict__['_normalize'] = func

    if _has_UserDict_base: # Robot 2.8
        @property
        def normalized(self):
            return self.data

    else: # Robot 2.9
        @property
        def normalized(self):
            return self._data


def normdictclass(typename='NormalizedDict',
  ignore='', caseless=True, spaceless=True, base=NormalizedDict):

    if not issubclass(base, NormalizedDict):
        raise TypeError("'base' is no subclass of normdictclass.base: %s"
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

    clsattrs = {}
    if base.__init__ is NormalizedDict.__init__:
        #==> no custom __init__ in custom base class
        #==> create default __init__ without normalizing options
        #    from basic robot.utils.NormalizedDict.__init__

        def __init__(self, mapping, **items):
            base.__init__(self, mapping)
            if items:
                self.update(items)

        clsatrs['__init__'] = __init__

    return Type(typename, (base,), clsattrs)

normdictclass.base = NormalizedDict
normdicttype = normdictclass


def normdictkeys(nd):
    """Iterate the internal mormalized keys
       of :class:`robot.utils.NormalizedDict` instance `nd`.
    """
    if not isinstance(nd, base):
        raise TypeError(
          "normdictkeys() arg must be a robot.utils.NormalizedDict instance")
    return iterkeys(nd.data if _has_UserDict_base else nd._data)


def normdictitems(nd):
    """Iterate the internal items with normalized keys
       of :class:`robot.utils.NormalizedDict` instance `nd`
    """
    if not isinstance(nd, base):
        raise TypeError(
          "normdictitems() arg must be a robot.utils.NormalizedDict instance")
    return iteritems(nd.data if _has_UserDict_base else nd._data)


def normdictdata(nd):
    """Get the internal data dict with normalized keys
       of :class:`robot.utils.NormalizedDict` instance `nd`
    """
    if not isinstance(nd, base):
        raise TypeError(
          "normdictdata() arg must be a robot.utils.NormalizedDict instance")
    return nd.data if _has_UserDict_base else nd._data
