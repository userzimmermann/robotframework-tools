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

"""robottools.library.inspector.keyword

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['KeywordInspector']

from .arguments import KeywordArgumentsInspector


class KeywordInspector(object):
    def __init__(self, handler):
        self._handler = handler

    @property
    def __doc__(self):
        return "%s\n\n%s" % (repr(self), self._handler.doc)

    @property
    def arguments(self):
        return KeywordArgumentsInspector(self._handler.arguments)

    def __getattr__(self, name):
        return getattr(self._handler, name)

    def __dir__(self):
        return ['name', 'doc', 'shortdoc']

    def __str__(self):
        return self._handler.longname

    def __repr__(self):
        return '[Keyword] %s [ %s ]' % (self, self.arguments)
