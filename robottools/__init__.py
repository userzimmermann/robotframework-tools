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
__all__ = 'LibraryType', 'library',

from collections import OrderedDict
from moretools import simpledict

from .keywords import KeywordsDict

class LibraryType(object):
  """A base class for Robot Test Libraries.
  * Should not be initialized directly.
  * :func:`library` dynamically creates derived Library classes
  for use as a base for an actual Test Library.
  * Provides a decorator for declaring methods as Robot Keywords
  and storing them in a class owned `Keywords` mapping instance.
  """
  @classmethod
  def keyword(cls, func, name = None):
    """The Keyword method decorator.
    * When manually called with `()` an optional override `name` can be given.
    * The Keyword method function gets stored
    in the Library's `keywords` class attribute.
    ** This :class:`KeywordsDict` instance gets dynamically created
    for the derived Library `cls` in :func:`library`.
    """
    cls.keywords[name or func.func_name] = func
    return func

  def get_keyword_names(self):
    """Get all lower_case Keyword names for Robot Framework
    from `self.keywords` mapping.
    """
    return [name for name, method in self.keywords]

  def __init__(self):
    """Initializes the Test Library base.
    * Creates a new `Keywords` mapping
    for storing the actual bound Keyword method objects
    corresponding to the method function objects
    in the Library class owned `Keywords` mapping
    populated by the `keyword` decorator.
    """
    self.keywords = KeywordsDict()
    for name, func in type(self).keywords:
      self.keywords[name] = getattr(self, name)

  def __getattr__(self, name):
    """CamelCase access to the bound Keyword methods.
    """
    return getattr(self.keywords, name)

  def __dir__(self):
    """Return the CamelCase Keyword names.
    """
    return dir(self.keywords)

# ordered name-mapped storing of user-defined session handlers
HandlersDict = simpledict('HandlersDict', dicttype = OrderedDict)

def library(session_handlers = []):
  """Creates the actual base type for a user-defined Robot Test Library
  derived from :class:`LibraryType`.

  For every handler in `session_handlers`
  its generated open_/switch_/close_session Keywords
  (with `Handler.meta.identifier_name` substituting 'session')
  will be added to the Library's Keywords.

  :returns: type.
  """
  # the attrs dict for type(...)
  clsattrs = {}

  # The Library's Keyword method function objects mapping
  # to be filled with the session handlers' Keywords
  # and further populated by the LibraryType.keyword decorator
  keywords = clsattrs['keywords'] = KeywordsDict()

  handlers = clsattrs['session_handlers'] = HandlersDict()
  for handlercls in session_handlers:
    handlers[handlercls.__name__] = handlercls
    # import the handler-specific session exception type
    clsattrs[handlercls.SessionError.__name__] = handlercls.SessionError
    # give access to the handler's dictionary of running sessions
    clsattrs[handlercls.meta.plural_identifier_name] = property(
      lambda self, h = handlercls: h.sessions)
    # give access to the handler's currently active session
    clsattrs[handlercls.meta.identifier_name] = property(
      lambda self, h = handlercls: h.session)
    # import the handler's auto-generated keywords
    for keywordname, func in handlercls.keywords:
      clsattrs[keywordname] = keywords[keywordname] = func

  return type('Library', (LibraryType,), clsattrs)
