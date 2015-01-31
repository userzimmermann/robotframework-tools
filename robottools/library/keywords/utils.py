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

"""robottools.keywords.utils

Keyword name/storage/access handling.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import PY3

__all__ = ['KeywordName', 'KeywordsDict']

from moretools import simpledict, camelize

from robot.utils import normalize


class KeywordName(str):
    """:class:`str` wrapper to work with Keyword names in a Robot way.

    - Converts the given raw Keyword name (usually a function name)
      to Capitalized Robot Style.
    - Uses :func:`robot.utils.normalize`d conversions
      (plain lowercase without spaces and underscores)
      for comparing and hashing.
    """
    def __new__(cls, name, convert=True):
        if convert and type(name) is not KeywordName:
            name = camelize(name, joiner=' ')
        return str.__new__(cls, name)

    @property
    def normalized(self):
        return normalize(self, ignore='_')

    def __eq__(self, name):
        return self.normalized == normalize(name, ignore='_')

    def __hash__(self):
        return hash(self.normalized)


class KeywordsDict(object):
    """Store Keyword functions or :class:`Keyword` objects
       with :class:`KeywordName` keys.
    """
    def __init__(self):
        self._dict = {}

    def __setitem__(self, name, keyword):
        self._dict[KeywordName(name)] = keyword

    def __getitem__(self, name):
        return self._dict[normalize(name, ignore='_')]

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __iter__(self):
        return iter(self._dict.items())

    def __len__(self):
        return len(self._dict)

    def __bool__(self):
        return bool(self._dict)

    def __nonzero__(self):
        return self.__bool__()

    def __dir__(self):
        """The Keyword names in CamelCase.
        """
        return [''.join(name.split()) for name in self._dict]
