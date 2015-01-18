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

"""robottools.library.base

Defines base class for Dynamic Test Libraries.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestLibraryType']

from textwrap import dedent

from decorator import decorator

from .keywords import Keyword, KeywordsDict


def check_keywords(func):
    """Decorator for Test Library methods,
    which checks if an instance-bound .keywords mapping exists.
    """
    def caller(func, self, *args, **kwargs):
        if self.keywords is type(self).keywords:
            raise RuntimeError(dedent("""
              '%s' instance has no instance-bound .keywords mapping.
              Was Test Library's base __init__ called?
              """ % type(self).__name__))

        return func(self, *args, **kwargs)

    return decorator(caller, func)


class TestLibraryType(object):
    """A base class for Robot Test Libraries.

    - Should not be initialized directly.
    - :func:`testlibrary` dynamically creates derived classes
      to use as (a base for) a custom Test Library.
    """

    @check_keywords
    def get_keyword_names(self):
        """Get all Capitalized Keyword names.

        - Part of Robot Framework's Dynamic Test Library API.
        """
        return [str(name) for name, kw in self.keywords]

    @check_keywords
    def run_keyword(self, name, args, kwargs={}):
        """Run the Keyword given by its `name`
        with the given `args` and optional `kwargs`.

        - Part of Robot Framework's Dynamic Test Library API.
        """
        keyword = self.keywords[name]
        return keyword(*args, **kwargs)

    @check_keywords
    def get_keyword_documentation(self, name):
        """Get the doc string of the Keyword given by its `name`.

        - Part of Robot Framework's Dynamic Test Library API.
        """
        if name == '__intro__':
            #TODO
            return ""
        if name == '__init__':
            #TODO
            return ""
        keyword = self.keywords[name]
        return keyword.__doc__

    @check_keywords
    def get_keyword_arguments(self, name):
        """Get the arguments definition of the Keyword given by its `name`.

        - Part of Robot Framework's Dynamic Test Library API.
        """
        keyword = self.keywords[name]
        return list(keyword.args())

    def __init__(self):
        """Initializes the Test Library base.

        - Creates a new :class:`KeywordsDict` mapping
          for storing bound :class:`Keyword` instances
          corresponding to the method function objects
          in the Test Library class' :class:`KeywordsDict` mapping,
          which was populated by the <Test Library class>.keyword decorator.
        - Sets the initially active contexts.
        """
        self.contexts = []
        for name, handler in self.context_handlers:
            self.contexts.append(handler.default)

        self.keywords = KeywordsDict()
        for name, func in type(self).keywords:
            self.keywords[name] = Keyword(name, func, libinstance=self)

    @check_keywords
    def __getattr__(self, name):
        """CamelCase access to the bound :class:`Keyword` instances.
        """
        try:
            return getattr(self.keywords, name)
        except AttributeError:
            raise AttributeError(
              "'%s' instance has no attribute or Keyword '%s'"
              % (type(self).__name__, name))

    @check_keywords
    def __dir__(self):
        """Return the CamelCase Keyword names.
        """
        return dir(self.keywords)
