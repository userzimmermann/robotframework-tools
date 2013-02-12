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

"""robottools.session

The Robot Test Library session handler framework.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = 'Handler',

import re

from .keywords import KeywordsDict

class Meta(object):
  """The meta information for a session handler
  based on the handler's class name
  and a user-defined `Handler.Meta` class.
  """
  def __init__(self, handlerclsname = None, defs = None):
    """Generate several variants of the session handler name
    for use in identifiers and message strings,
    based on the `handlerclsname`
    and/or the attributes of a `defs` class,
    which can define name (variant) prefixes/suffixes
    and/or explicit name variants.
    """
    def gen_prefix(key, default, append = ''):
      """Check the prefix definition for name variant identified by `key`,
      setting to `default` if not defined.
      Always `append` the given extra string.
      """
      try:
        prefix = getattr(defs, (key and key + '_') + 'name_prefix')
      except AttributeError:
        prefix = default
      else:
        prefix = prefix and str(prefix) or ''
      if prefix:
        prefix += append
      return prefix

    # check all prefix definitions and generate actual prefix strings
    prefix = {}
    prefix[''] = gen_prefix('', '', '_')
    prefix['upper'] = gen_prefix('upper', prefix[''].capitalize())
    prefix['identifier'] = gen_prefix('identifier', '', '_')
    prefix['upper_identifier'] = gen_prefix(
      'upper_identifier', prefix['identifier'].capitalize())
    prefix['verbose'] = gen_prefix('verbose', '', ' ')

    def gen_suffix(key, default, prepend = ''):
      """Check the suffix definition for name variant identified by `key`,
      setting to `default` if not defined.
      Always `prepend` the given extra string.
      """
      try:
        suffix = getattr(defs, key + '_name_suffix')
      except AttributeError:
        suffix = default
      else:
        suffix = suffix and str(suffix) or ''
      if suffix:
        suffix = prepend + suffix
      return suffix

    # check all suffix definitions and generate actual suffix strings
    suffix = {}
    suffix[''] = gen_suffix('', '', '_')
    suffix['upper'] = gen_suffix('upper', suffix[''].capitalize())
    suffix['identifier'] = gen_suffix('identifier', 'session', '_')
    suffix['upper_identifier'] = gen_suffix(
      'upper_identifier', suffix['identifier'].capitalize())
    suffix['verbose'] = gen_suffix('verbose', 'Session', ' ')

    # check explicit base name definition
    name = getattr(defs, 'name', None)
    # non-empty string or None
    name = name and str(name) or None
    # check all explicit name variant definitions
    variants = {}
    for variantkey in (
      'upper', 'identifier', 'plural_identifier', 'upper_identifier',
      'verbose', 'plural_verbose'
      ):
      variant = getattr(defs, variantkey + '_name', None)
      # non-empty string or None
      variant = variant and (str(variant) or None) or None
      variants[variantkey] = variant

    key = ''
    self.name = (
      name
      or prefix[key] + handlerclsname.lower() + suffix[key])
    key = 'upper'
    self.upper_name = (
      variants[key]
      or name and name.capitalize()
      or prefix[key] + handlerclsname + suffix[key])
    key = 'identifier'
    self.identifier_name = (
      variants[key]
      or prefix[key] + self.name + suffix[key])
    key = 'plural_identifier'
    self.plural_identifier_name = (
      variants[key]
      or self.identifier_name + 's')
    key = 'upper_identifier'
    self.upper_identifier_name = (
      variants[key]
      or prefix[key] + self.upper_name + suffix[key])
    key = 'verbose'
    self.verbose_name = (
      variants[key]
      or prefix[key] + self.upper_name + suffix[key])
    key = 'plural_verbose'
    self.plural_verbose_name = (
      variants[key]
      or self.verbose_name + 's')

class HandlerMeta(type):
  """The custom type class for :class:`Handler`.
  * For user-derived handler classes
  it generates the handler specific meta information,
  session storage, the actual Robot Keywords for session management,
  and a session exception type.
  """
  def __new__(metacls, clsname, bases, clsattrs):
    """Generate meta information, session exception type,
    and session/keywords storage
    for :class:`Handler` derived classes.
    """
    if clsname == 'Handler': # the handler base class itself
      return type.__new__(metacls, clsname, bases, clsattrs)

    try: # has a user-defined `Handler.Meta` class?
      metadefs = clsattrs['Meta']
    except KeyError:
      meta = Meta(handlerclsname = clsname)
    else:
      meta = Meta(handlerclsname = clsname, defs = metadefs)
    clsattrs['meta'] = meta

    excname = meta.upper_identifier_name + 'Error'
    clsattrs['SessionError'] = type(excname, (RuntimeError,), {})

    # The handler's dictionary of opened sessions
    clsattrs['sessions'] = {}
    # The handler's currently active session
    clsattrs['session'] = None

    # for storing the handler's session management Keywords
    clsattrs['keywords'] = KeywordsDict()

    return type.__new__(metacls, clsname, bases, clsattrs)

  def add_opener(cls, func):
    """Add Keywords for opening (un)named sessions
    for a user-defined session opener method `func`
    (methods whose names start with 'open').
    """
    suffix = re.sub('^open($|_)', '', func.func_name)
    keywordname = 'open%s_' + cls.meta.identifier_name
    if suffix:
      keywordname += '_' + suffix

    def open_session(self, *args, **kwargs):
      """Open an unnamed session.
      (Automatically closes already running unnamed sessions.)
      """
      session = func(self, *args, **kwargs)
      cls.add_session(session)

    cls.keywords[keywordname % ''] = open_session

    def open_named_session(self, name, *args, **kwargs):
      """Open a named session.
      (Automatically closes running unnamed sessions.)
      """
      session = func(self, *args, **kwargs)
      cls.add_named_session(name, session)

    cls.keywords[keywordname % '_named'] = open_named_session

  def __init__(cls, clsname, bases, clsattrs):
    """Generate the actual session management keywords
    for :class:`Handler` derived classes,
    based on the session management helper methods of :class:`Handler`
    and user-defined session opener methods (whose names start with 'open').
    All Keyword names include the handler specific `meta.identifier_name`.
    """
    try:
      meta = cls.meta
    except AttributeError:
      return

    for func in clsattrs.values():
      try:
        name = func.func_name
      except AttributeError: # no function object
        pass
      else:
        if name.startswith('open'):
          cls.add_opener(func)

    def switch_session(self, name):
      cls.switch_session(name)

    keywordname = 'switch_' + meta.identifier_name
    cls.keywords[keywordname] = switch_session

    def close_session(self):
      cls.close_session()

    keywordname = 'close_' + meta.identifier_name
    cls.keywords[keywordname] = cls.close_session

class Handler(object):
  """The base class for custom Robot Test Library session handler types.
  """
  __metaclass__ = HandlerMeta

  @classmethod
  def add_session(cls, session):
    """Helper method for adding an unnamed session to the handler
    and making it active.
    (Automatically closes already running unnamed sessions.)
    """
    cls.session = session

  @classmethod
  def add_named_session(cls, name, session):
    """Helper method for adding a named session to the handler
    and making it active.
    (Automatically closes running unnamed sessions.)
    """
    name = str(name)
    cls.session = cls.sessions[name] = session

  @classmethod
  def switch_session(cls, name):
    """Helper method for switching the currently active session.
    (Automatically closes running unnamed sessions.)
    """
    name = str(name)
    try:
      cls.session = cls.sessions[name]
    except KeyError:
      raise cls.SessionError('Session not found: %s' % repr(name))

  @classmethod
  def close_session(cls):
    """Helper method for closing the currently active session.
    """
    if cls.session is None:
      raise cls.SessionError('No active session.')
    for name, session in cls.sessions.items():
      if session is cls.session:
        del cls.sessions[name]
    cls.session = None
