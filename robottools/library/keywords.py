# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""robottools.keywords

- Provides a `moretools.simpledict` mapping type
  for storing Robot Test Library Keyword methods,
  provding dynamic Test-Case-like CamelCase access for interactive use.

- Defines the Test Library Keyword decorator base class
  which is used to identify methods as Robot Keywords
  and to apply certain additional options to these methods.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = [
  'KeywordsDict', 'Keyword',
  'KeywordDecoratorType', 'InvalidKeywordOption']

import inspect
import re
from itertools import chain

from moretools import simpledict, camelize, decamelize

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

    def __init__(self, name, convert=True):
        self.normalized = normalize(name, ignore='_')

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

    def __dir__(self):
        """The Keyword names in CamelCase.
        """
        return [''.join(name.split()) for name in self._dict]

class Keyword(object):
    def __init__(self, name, func, libinstance):
        self.name = name
        self.func = func
        self.libinstance = libinstance

    @property
    def __doc__(self):
        return self.func.__doc__

    @property
    def libname(self):
        return type(self.libinstance).__name__

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name)

    def args(self):
        # First look for custom override args list:
        if self.func.args:
            for arg in self.func.args:
                yield arg
            return

        argspec = self.func.argspec
        posargs = argspec.args[1:]
        defaults = argspec.defaults
        if defaults:
            for arg, defaults_index in zip(
              posargs, range(-len(posargs), 0)
              ):
                try:
                    default = defaults[defaults_index]
                except IndexError:
                    yield arg
                else:
                    yield '%s=%s' % (arg, default)
        else:
            for arg in posargs:
                yield arg
        if argspec.varargs:
            yield '*' + argspec.varargs
        if argspec.keywords:
            yield '**' + argspec.keywords

    def __call__(self, *args, **kwargs):
        func = self.func
        for context, context_func in func.contexts.items():
            if context in self.libinstance.contexts:
                func = context_func
        if self.func.argspec.keywords or not kwargs:
            return func(self.libinstance, *args, **kwargs)
        ikwargs = ('%s=%s' % item for item in kwargs.items())
        return func(self.libinstance, *chain(args, ikwargs))

    def __repr__(self):
        return '%s [ %s ]' % (self.longname, ' | '.join(self.args()))

class InvalidKeywordOption(LookupError):
    pass

class KeywordNotDefined(LookupError):
    pass

class KeywordDecoratorType(object):
    """The base type for a Test Library's `keyword` decorator.

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
        """Creates a wrapper method for Keyword method `func`
           which converts all unicode args to str.
        """
        def method(self, *args, **kwargs):
            iargs = (type(a) is unicode and str(a) or a for a in args)
            return func(self, *iargs, **kwargs)

        method.func_name = func.func_name
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
        doc = func.func_doc
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
            name = self.keyword_name or func.func_name
        if func.func_doc:
            # Update saved doc string
            doc = func.func_doc

        # Use at least one wrapper to make the assignments below always work
        def keyword_method(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        # Keep existing (or explicitly given) method name
        keyword_method.func_name = name
        # Keep method doc string
        keyword_method.func_doc = doc
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
