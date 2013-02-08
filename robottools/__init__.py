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

__all__ = 'SessionError', 'LibraryBase', 'library',

import re

from moretools import simpledict

class SessionError(RuntimeError):
  """Standard Exception for Robot Library session handling related errors.
  """
  pass

# A mapping type for storing Robot Library Keyword methods by name,
# providing additional `__getattr__` access with CamelCase Keyword names
Keywords = simpledict(
  'Keywords',
  # convert lower_case keyword names to CamelCase attribute names
  key_to_attr = lambda key: re.sub(
    '_([a-z])', lambda match: match.group(1).upper(),
    key.capitalize()),
  # convert CamelCase keyword attribute names back to lower_case
  attr_to_key = lambda name: re.sub(
    '[A-Z]', lambda match: '_' + match.group().lower(),
    name[0].lower() + name[1:]))

class LibraryBase(object):
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
    ** This :class:`Keywords` instance gets dynamically created
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
    self.keywords = Keywords()
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

def library(session_groups = []):
  """Creates the actual base type for a Robot Test Library
  derived from :class:`LibraryBase`.

  For every name in `session_groups`
  a session handling system will be generated.
  This includes a decorator `<group name>_opener`
  for turning session open methods to
  `open_<group name>`/`open_named_<group name>` Keywords
  (with optional suffixes based on the method name),
  a `<group name>` property
  for accessing the currently active session,
  a `switch_<group name>` Keyword for switching the currently active session,
  and a `close_<group name>` Keyword.

  :returns: type.
  """
  # The Library's dictionary of opened-sessions-by-group-dictionaries
  sessions = {}
  # The Library's Keyword method function objects mapping
  # to be populated by the keyword decorator
  keywords = Keywords()
  clsattrs = dict( # for the type('Library', (LibraryBase,), clsattrs) call
    sessions = sessions,
    # the currently active sessions of the session groups
    sessionnames = {},
    keywords = keywords,
    )
  for group in session_groups:
    # the group's dictionary of opened sessions
    sessions[group] = {}

    def register_session(self, session):
      """Helper method for registering an unnamed session of `group`
      to the `Library.sessions` dictionary.
      """
      self.sessions[group][None] = session
      self.sessionnames[group] = None

    clsattrs['register_' + group] = register_session

    def register_named_session(self, name, session):
      """Helper method for registering a named session of `group`
      to the `Library.sessions` dictionary.
      """
      self.sessions[group][name] = session
      self.sessionnames[group] = name

    clsattrs['register_named_' + group] = register_named_session

    def session(self):
      """Property method for accessing
      the currently active session of `group`.
      """
      sessions = self.sessions[group]
      try:
        name = self.sessionnames[group]
      except KeyError: # no active session name (or None for unnamed)
        raise SessionError('No Session opened yet.')
      try:
        return sessions[name]
      except KeyError:
        raise RuntimeError(
          name is None and 'No unnamed Session.'
          or 'Session not found: %s' % name)

    clsattrs[group] = property(session)

    def opener(cls, openfunc):
      """The Library `cls`'s decorator
      for turning method functions to named/unnamed session open Keywords.
      """
      # optional `open_<group>` Keyword suffix based on method name
      suffix = openfunc.func_name.lstrip('_')

      def open_session(self, *args, **kwargs):
        """Open an unnamed session.
        """
        session = openfunc(self, *args, **kwargs)
        register = getattr(self, 'register_' + group)
        register(session)

      keywordname = 'open_' + group
      if suffix:
        keywordname += '_' + suffix
      setattr(
        cls, keywordname, cls.keyword( # call decorator with override name
          open_session, name = keywordname))

      def open_named_session(self, name, *args, **kwargs):
        """Open a named session.
        Automatically closes running unnamed sessions.
        """
        session = openfunc(self, *args, **kwargs)
        register = getattr(self, 'register_named_' + group)
        register(name, session)
        try: # close an unnamed session if running
          del self.sessions[group][None]
        except KeyError:
          pass

      keywordname = 'open_named_' + group
      if suffix:
        keywordname += '_' + suffix
      setattr(
        cls, keywordname, cls.keyword( # call decorator with override name
          open_named_session, name = keywordname))

    clsattrs[group + '_opener'] = classmethod(opener)

    def switch_session(self, name = None):
      """Switch the currently active session.
      Automatically closes running unnamed sessions.
      """
      sessions = self.sessions[group]
      name = str(name)
      if name not in sessions:
        raise SessionError('Session not found: %s' % name)
      self.sessionnames[group] = name
      try: # close an unnamed session if running
        del sessions[None]
      except KeyError:
        pass

    keywordname = 'switch_' + group
    clsattrs[keywordname] = keywords[keywordname] = switch_session

    def close_session(self):
      """Close the currently active session.
      """
      sessions = self.sessions[group]
      name = self.sessionnames[group]
      try:
        del sessions[name]
      except KeyError:
        raise RuntimeError(
          name is None and 'No unnamed Session.'
          or 'Session not found: %s' % name)

    keywordname = 'close_' + group
    clsattrs[keywordname] = keywords[keywordname] = close_session

  return type('Library', (LibraryBase,), clsattrs)
