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

Create custom NormalizedDict classes with pre-defined normalizing options
and access internal normalized data of NormalizedDict instances.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['NormalizedDict', 'normdictclass', 'normdicttype',
           'normdictkeys', 'normdictitems', 'normdictdata']

from six import with_metaclass, iterkeys, iteritems
from six.moves import UserString, UserDict

from moretools import qualname
import modeled

from robot.utils import normalize, NormalizedDict as base


# check for Robot 2.8
_has_UserDict_base = issubclass(base, UserDict)


class meta(modeled.object.meta,
           # avoid metaclass conflicts
           type(base) if issubclass(base, object) else type
           ):
    """Metaclass for basic :class:`robottools.utils.NormalizedDict`

    - Enables derived classes to pre-define normalizing options
      via meta attributes.
    """
    # default normalizing options
    ignore = ''
    caseless = True
    spaceless = True

    def __init__(cls, clsname, bases, clsattrs):
        modeled.object.meta.__init__(cls, clsattrs, bases, clsattrs)

        # to be stored as .normalize metamethod of created class
        def normalizer(value):
            """Normalize `value` based on normalizing options from metaclass.
            """
            if isinstance(value, UserString):
                value = value.data
            return normalize(value, ignore=cls.ignore,
              caseless=cls.caseless, spaceless=cls.spaceless)

        normalizer.__qualname__ = '%s.meta.normalize' % qualname(cls)
        cls.meta.normalize = staticmethod(normalizer)

        if cls.__init__ is modeled.object.__init__:
            #==> no custom cls.__init__
            #==> create default __init__ without normalizing options
            #    from basic robot.utils.NormalizedDict.__init__

            def __init__(self, mapping, **items):
                modeled.object.__init__(self)
                base.__init__(self, mapping)
                if items:
                    self.update(items)

            cls.__init__ = __init__


class NormalizedDict(with_metaclass(meta, modeled.object, base)):

    def __init__(self, mapping=None):
        """Only initialize with an optional `mapping`
           and no normalizing options.
        """
        base.__init__(self, mapping)

    #HACK: internally used by robot.utils.NormalizedDict base
    # (normally dynamically created and assigned in base __init__)
    @property
    def _normalize(self):
        return type(self).normalize

    #HACK: avoid an exception when base __init__ tries to set
    # the internal _normalize function
    @_normalize.setter
    def _normalize(self, func):
        pass

    # define a common .normalized property
    # for accessing the internal dict with normalized keys
    #!!! those keys should not be manipulated manually !!!
    if _has_UserDict_base: # Robot 2.8
        @property
        def normalized(self):
            return self.data

    else: # Robot 2.9
        @property
        def normalized(self):
            return self._data


def normdictclass(typename='NormalizedDict',
  ignore='', caseless=True, spaceless=True, base=NormalizedDict
  ):
    if not issubclass(base, NormalizedDict):
        raise TypeError("'base' is no subclass of normdictclass.base: %s"
                        % base)

    cls = type(NormalizedDict)(typename, (base,), {})
    meta = cls.meta
    # store the normalizing options
    meta.ignore = ignore
    meta.caseless = caseless
    meta.spaceless = spaceless
    return cls


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
