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

"""robottools.library.keywords.deco

testlibrary's @keyword decorator base class.

- Used to identify methods as Robot Keywords
  and to apply certain additional options to these methods.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import PY3

__all__ = ['KeywordDecoratorType']

import inspect

from robot.utils import NormalizedDict

from robottools.utils import normdictdata

from .utils import KeywordName
from .errors import InvalidKeywordOption, KeywordNotDefined


def create_dictionary(*args, **items):
    iargs = iter(args)
    return dict(zip(iargs, iargs), **items)


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
           and custom `meta` info like name and args list overrides
           and explicit argtypes for automatic type conversions.
        """
        self.keywords = keywords

        for optionname in options:
            if not hasattr(type(self), 'option_' + optionname):
                raise InvalidKeywordOption(optionname)
        self.options = options

        name = meta.get('name')
        self.keyword_name = name and KeywordName(name, convert=False)
        self.keyword_args = meta.get('args')
        self.keyword_argtypes = meta.get('argtypes')
        self.contexts = meta.get('contexts')

    def __getitem__(self, argtypes):
        return type(self)(
          self.keywords, *self.options,
          name=self.keyword_name, args=self.keyword_args,
          argtypes=argtypes, contexts=self.contexts)

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

    @staticmethod
    def option_varargs_to_kwargs(func):
        # try:
        #     argspec = func.argspec
        # except AttributeError:
        #     argspec = inspect.getargspec(func)
        nposargs = len(func.argspec.args) - 1 # without self

        def method(self, *args, **kwargs):
            posargs = args[:nposargs]
            varargs = args[nposargs:]
            kwargs = create_dictionary(*varargs, **kwargs)
            return func(self, *posargs, **kwargs)

        method.__name__ = func.__name__
        return method

    @staticmethod
    def option_normalized_kwargs(func):
        """Normalize the keys of **kwargs using robot.utils.NormalizedDict
           (convert to lowercase and remove spaces).
        """
        def method(self, *args, **kwargs):
            kwargs = NormalizedDict(kwargs)
            return func(self, *args, **normdictdata(kwargs))

        method.__name__ = func.__name__
        return method

    @property
    def no_options(self):
        return type(self)(self.keywords)

    @property
    def reset_options(self):
        return type(self)(self.keywords)

    def __getattr__(self, optionname):
        """Returns a new Keyword decorator class instance
           with the given option added.
        """
        if not hasattr(type(self), 'option_' + optionname):
            raise AttributeError(optionname)
        return type(self)(
          self.keywords, optionname, *self.options,
          name=self.keyword_name, args=self.keyword_args,
          argtypes=self.keyword_argtypes, contexts=self.contexts)

    def __call__(self, func=None, name=None, args=None, argtypes=None,
                 contexts=None):
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
              self.keywords, *self.options, name=name, args=args,
              argtypes=argtypes, contexts=contexts)

        original_func = func
        if self.contexts:
            for context in self.contexts:
                context(func)
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

        # Use at least one wrapper to make attribute assignments always work
        def func(self, *args, **kwargs):
            return original_func(self, *args, **kwargs)

        func.__name__ = original_func.__name__
        func.argspec = argspec
        # Apply options
        for optionname in self.options:
            decorator = getattr(type(self), 'option_' + optionname)
            func = decorator(func)
            try: # does returned function still have argspec attribute?
                # (unchanged function or option has assigned new argspec)
                argspec = func.argspec
            except AttributeError:
                # Store previous argspec
                func.argspec = argspec
        if name:
            name = KeywordName(name, convert=False)
        else:
            name = self.keyword_name or func.__name__
        if func.__doc__:
            # Update saved doc string
            doc = func.__doc__

        # Keep existing (or explicitly given) method name
        func.__name__ = name
        # Keep method doc string
        func.__doc__ = doc
        # # Store original method argspec
        # func.argspec = argspec
        # Store optional override args list and explicit argtypes
        func.args = args or self.keyword_args
        func.argtypes = argtypes or self.keyword_argtypes
        # Add method to the Library's Keywords mapping
        if contexts:
            try:
                keyword = self.keywords[name]
            except KeyError:
                raise KeywordNotDefined(name)
            for context in contexts:
                keyword.contexts[context] = func
        else:
            func.contexts = {}
            self.keywords[name] = func

        return original_func
