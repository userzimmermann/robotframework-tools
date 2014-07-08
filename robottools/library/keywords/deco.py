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

"""robottools.library.keywords.deco

testlibrary's @keyword decorator base class.

- Used to identify methods as Robot Keywords
  and to apply certain additional options to these methods.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import PY3

__all__ = ['KeywordDecoratorType']

import inspect

from .utils import KeywordName
from .errors import InvalidKeywordOption, KeywordNotDefined


class KeywordDecoratorType(object):
    """The base class for a Test Library's `keyword` decorator.

    - Stores the Keyword method function
      in the Test Library's `keywords` mapping,
      after applying additional options (decorators) to the function.
    - Options are added with `__getattr__`,
      which generates new decorator class instances.
    """
    def __init__(self, keywords, *options, **meta):
        """Initialize with a Test Library's :class:`KeywordsDict` instance,
           additional `options` to apply to the decorated methods
           and custom `meta` info like name and args list overrides.
        """
        self.keywords = keywords

        for optionname in options:
            if not hasattr(type(self), 'option_' + optionname):
                raise InvalidKeywordOption(optionname)
        self.options = options

        name = meta.get('name')
        self.keyword_name = name and KeywordName(name, convert=False)
        self.keyword_args = meta.get('args')

    @staticmethod
    def option_unicode_to_str(func):
        """[PY2] Creates a wrapper method for Keyword method `func`
           which converts all unicode args to str.
        """
        if PY3:
            return func

        def method(self, *args, **kwargs):
            iargs = (type(a) is unicode and str(a) or a for a in args)
            return func(self, *iargs, **kwargs)

        method.__name__ = func.__name__
        return method

    @property
    def no_options(self):
        return type(self)(self.keywords)

    @property
    def reset_options(self):
        return type(self)(self.keywords)

    def __getattr__(self, name):
        """Returns a new Keyword decorator class instance
           with the given option added.
        """
        if not hasattr(type(self), 'option_' + name):
            raise AttributeError(name)
        return type(self)(self.keywords, name, *self.options)

    def __call__(self, func=None, name=None, args=None):
        """The actual Keyword method decorator function.

        - When manually called, optional override `name`
          and `args` list can be given.
        - If `func` is None a new decorator instance
          with stored `name` and `args` is returned.
        - All Keyword options added to this decorator class instance
          are applied.
        - The Keyword method function is stored
          in the Test Library's `keywords` mapping.
        """
        if not func:
            return type(self)(
              self.keywords, *self.options, name=name, args=args)

        original_func = func
        try:
            contexts = func.contexts
        except AttributeError:
            contexts = None
        # Save original doc string
        doc = func.__doc__
        try:
            argspec = func.argspec
        except AttributeError:
            argspec = inspect.getargspec(func)
        # Apply options
        for optionname in self.options:
            decorator = getattr(type(self), 'option_' + optionname)
            func = decorator(func)
        if name:
            name = KeywordName(name, convert=False)
        else:
            name = self.keyword_name or func.__name__
        if func.__doc__:
            # Update saved doc string
            doc = func.__doc__

        # Use at least one wrapper to make the assignments below always work
        def keyword_method(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        # Keep existing (or explicitly given) method name
        keyword_method.__name__ = name
        # Keep method doc string
        keyword_method.__doc__ = doc
        # Store original method argspec
        keyword_method.argspec = argspec
        # Store optional override args list
        keyword_method.args = args or self.keyword_args
        # Add method to the Library's Keywords mapping
        if contexts:
            try:
                keyword = self.keywords[name]
            except KeyError:
                raise KeywordNotDefined(name)
            for context in contexts:
                keyword.contexts[context] = keyword_method
        else:
            keyword_method.contexts = {}
            self.keywords[name] = keyword_method

        return original_func
