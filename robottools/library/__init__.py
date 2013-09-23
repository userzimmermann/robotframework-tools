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

"""robottools

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = (
  'TestLibraryType', 'testlibrary',
  # from .keywords
  'KeywordDecoratorType', 'InvalidKeywordOption',
  )

from functools import partial
from collections import OrderedDict
from moretools import simpledict

from .keywords import (
  KeywordsDict, Keyword,
  KeywordDecoratorType, InvalidKeywordOption,
  )

class TestLibraryType(object):
    """A base class for Robot Test Libraries.
    * Should not be initialized directly.
    * :func:`testlibrary` dynamically creates derived classes
    for use as a base for a custom Test Library.
    """
    def get_keyword_names(self):
        """Get all lower_case Keyword names for Robot Framework
        from the `self.keywords` mapping.
        """
        return [name for name, kw in self.keywords]

    def run_keyword(self, name, args, kwargs={}):
        """Run the Keyword given by its lower_case `name`
        with the given `args` and `kwargs`.
        """
        keyword = self.keywords[name]
        return keyword(*args, **kwargs)

    def get_keyword_documentation(self, name):
        """Get the doc string of the Keyword
        given by its lower_case `name`.
        """
        if name == '__intro__':
            return ""
        if name == '__init__':
            return ""
        keyword = self.keywords[name]
        return keyword.__doc__

    def get_keyword_arguments(self, name):
        """Get the arguments definition of the Keyword
        given by its lower_case `name`.
        """
        keyword = self.keywords[name]
        return list(keyword.args())

    def __init__(self):
        """Initializes the Test Library base.
        * Creates a new `KeywordsDict` instance
        for storing the actual bound Keyword method objects
        corresponding to the method function objects
        in the Test Library class-owned `KeywordsDict` instance
        populated by the `keyword` decorator.
        """
        self.contexts = []
        for name, handler in self.context_handlers:
            self.contexts.append(handler.default)

        self.keywords = KeywordsDict()
        for name, func in type(self).keywords:
            self.keywords[name] = Keyword(name, func, libinstance=self)

    def __getattr__(self, name):
        """CamelCase access to the bound Keyword methods.
        """
        return getattr(self.keywords, name)

    def __dir__(self):
        """Return the CamelCase Keyword names.
        """
        return dir(self.keywords)

# Ordered name-mapped storage of user-defined session/context handlers
HandlersDict = simpledict('HandlersDict', dicttype = OrderedDict)

def testlibrary(
  register_keyword_options = [],
  default_keyword_options = [],
  context_handlers = [],
  session_handlers = []
  ):
    """Creates the actual base type for a user-defined Robot Test Library
    derived from :class:`TestLibraryType`.

    * Generates a Keyword decorator class from `.keywords.KeywordDecoratorType`,
    adding the decorators from `register_keyword_options`.
    * Adds the `keyword` decorator to the Test Library class
    by instantiating the decorator class with the `default_keyword_options`.

    * For every handler in `session_handlers`
    its generated open_/switch_/close_session Keywords
    (with `Handler.meta.identifier_name` substituting 'session')
    will be added to the Test Library's Keywords.

    :returns: type.
    """
    # the attributes dict for the Test Library base class generation
    clsattrs = {}

    # The Test Library's Keyword method function objects mapping
    # to be filled with the session handlers' Keywords
    # and further populated by the TestLibraryType.keyword decorator
    keywords = clsattrs['keywords'] = KeywordsDict()

    # the attributes dict for the Keyword decorator class generation
    decotypeattrs = {}
    # the additional custom Keyword decorator options
    for decofunc in register_keyword_options:
        try:
            optionname = decofunc.func_name
        except AttributeError:
            optionname, decofunc = decofunc
        decotypeattrs['option_' + optionname] = staticmethod(decofunc)
    # create the final Keyword decorator
    decotype = type(
      'KeywordDecorator', (KeywordDecoratorType,), decotypeattrs)
    keyword_decorator = clsattrs['keyword'] = decotype(
      keywords, *default_keyword_options)

    handlers = clsattrs['context_handlers'] = HandlersDict()
    for handlercls in context_handlers:
        handlers[handlercls.__name__] = handlercls()

        # import the handler's auto-generated keywords
        for keywordname, func in handlercls.keywords:
            clsattrs[keywordname] = keyword_decorator(
              func, name=keywordname)

    handlers = clsattrs['session_handlers'] = HandlersDict()
    for handlercls in session_handlers:
        handlers[handlercls.__name__] = handlercls

        # import the handler-specific session exception type
        clsattrs[handlercls.SessionError.__name__
                 ] = handlercls.SessionError

        # give access to the handler's dictionary of running sessions
        clsattrs[handlercls.meta.plural_identifier_name] = property(
          lambda self, h=handlercls: h.sessions)

        # give access to the handler's currently active session
        def session(self, h = handlercls):
            if h.session is None:
                raise h.SessionError("No active session.")
            return h.session

        clsattrs[handlercls.meta.identifier_name] = property(session)

        # import the handler's auto-generated keywords
        for keywordname, func in handlercls.keywords:
            clsattrs[keywordname] = keyword_decorator(
              func, name=keywordname)

    return type('TestLibrary', (TestLibraryType,), clsattrs)
