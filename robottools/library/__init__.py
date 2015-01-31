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

"""robottools.library

Dynamic Test Library creation framework.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['testlibrary', 'istestlibraryclass',
  # from .base
  'TestLibraryType',
  # from .keywords
  'KeywordDecoratorType', 'InvalidKeywordOption',
  ]

from inspect import isclass
from collections import OrderedDict

from moretools import simpledict

from .base import TestLibraryType
from .keywords import (
  KeywordsDict, KeywordDecoratorType, InvalidKeywordOption)


# Ordered name-mapped storage of user-defined session/context handlers
HandlersDict = simpledict('HandlersDict', dicttype=OrderedDict)


def testlibrary(
  register_keyword_options=[],
  default_keyword_options=[],
  context_handlers=[],
  session_handlers=[]
  ):
    """Creates the actual base type for a user-defined Robot Test Library
       derived from :class:`TestLibraryType`.

    - Generates a Keyword decorator class
      from `.keywords.KeywordDecoratorType`,
      adding the decorators from `register_keyword_options`.
    - Adds the `keyword` decorator to the Test Library class
      by instantiating the decorator class with the `default_keyword_options`.
    - For every handler in `session_handlers`,
      its generated open_/switch_/close_session Keywords
      (with `Handler.meta.identifier_name` substituting 'session')
      will be added to the Test Library's Keywords.

    :returns: class
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
            optionname = decofunc.__name__
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

        # Create a property for getting the currently active context name:
        def context(self, _cls=handlercls):
            for current in self.contexts:
                if current.handler == _cls:
                    return current.name
            #TODO
            raise RuntimeError

        clsattrs[handlercls.__name__.lower()] = property(context)

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
        def session(self, h=handlercls):
            if h.session is None:
                raise h.SessionError("No active session.")
            return h.session

        clsattrs[handlercls.meta.identifier_name] = property(session)

        # import the handler's auto-generated keywords
        for keywordname, func in handlercls.keywords:
            clsattrs[keywordname] = keyword_decorator(
              func, name=keywordname)

    return type('TestLibrary', (TestLibraryType,), clsattrs)


def istestlibraryclass(cls):
    """Check if `cls` was created by :func:`testlibrary`.

    - Actually test if `cls` was derived from basic :class:`TestLibraryType`.
    """
    if not isclass(cls):
        return False
    return issubclass(cls, TestLibraryType)
