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

from moretools import camelize, decamelize

from .keywords import KeywordsDict

class Meta(object):
  """The meta information for a session handler
  based on the handler's class name
  and a user-defined `Handler.Meta` class.
  """
  def __init__(self, handlerclsname = None, metadefs = None):
    """Generate several variants of a session handler name
    for use in identifiers and message strings,
    based on the `handlerclsname`
    and/or the attributes of the optional `Handler.Meta` class in `metadefs`,
    which can define name (variant) prefixes/suffixes
    and/or explicit name variants.
    """
    # check all prefix definitions and generate actual prefix strings
    prefixes = {}

    def gen_prefix(key, default, append = ''):
      """Check the prefix definition for name variant identified by `key`,
      setting to `default` if not defined.
      Always `append` the given extra string.
      """
      try:
        prefix = getattr(metadefs, (key and key + '_') + 'name_prefix')
      except AttributeError:
        prefix = default
      else:
        prefix = prefix and str(prefix) or ''
      if prefix and not prefix.endswith(append):
        prefix += append
      # finally add to the prefixes dictionary
      prefixes[key] = prefix

    def gen_plural_prefix(key, append = ''):
      """Check the prefix definition
      for plural name variant identified by plural_`key`,
      setting to singular `key` prefix if not defined.
      Always `append` the given extra string.
      """
      plural_key = 'plural' + (key and '_' + key)
      default = prefixes[key]
      gen_prefix(plural_key, default, append)

    # base name prefixes
    gen_prefix('', '', '_')
    gen_plural_prefix('', '_')
    gen_prefix('upper', camelize(prefixes['']))
    gen_plural_prefix('upper')
    # identifier name prefixes
    gen_prefix('identifier', '', '_')
    gen_plural_prefix('identifier', '_')
    gen_prefix('upper_identifier', camelize(prefixes['identifier']))
    # verbose name prefixes
    gen_prefix('verbose', '', ' ')
    gen_plural_prefix('verbose', ' ')

    # check all suffix definitions and generate actual suffix strings
    suffixes = {}

    def gen_suffix(key, default, prepend = ''):
      """Check the suffix definition for name variant identified by `key`,
      setting to `default` if not defined.
      Always `prepend` the given extra string.
      """
      try:
        suffix = getattr(metadefs, key + '_name_suffix')
      except AttributeError:
        suffix = default
      else:
        suffix = suffix and str(suffix) or ''
      if suffix and not suffix.startswith(prepend):
        suffix = prepend + suffix
      # finally add to the suffixes dictionary
      suffixes[key] = suffix

    def gen_plural_suffix(key, prepend = ''):
      """Check the suffix definition
      for plural name variant identified by plural_`key`,
      setting to singular `key` suffix + 's' if not defined.
      Always `prepend` the given extra string.
      """
      plural_key = 'plural' + (key and '_' + key)
      default = suffixes[key] and suffixes[key] + 's'
      gen_suffix(plural_key, default, prepend)

    # identifier name suffixes
    gen_suffix('', '', '_')
    gen_plural_suffix('', '_')
    gen_suffix('upper', camelize(suffixes['']))
    gen_plural_suffix('upper')
    # identifier name suffixes
    gen_suffix('identifier', 'session', '_')
    gen_plural_suffix('identifier', '_')
    gen_suffix('upper_identifier', camelize(suffixes['identifier']))
    # verbose name suffixes
    gen_suffix('verbose', 'Session', ' ')
    gen_plural_suffix('verbose', ' ')

    # check explicit name variant definitions
    variants = {}
    for variantkey in (
      '', 'plural', 'upper', 'plural_upper',
      'identifier', 'plural_identifier', 'upper_identifier',
      'verbose', 'plural_verbose'
      ):
      defname = (variantkey and variantkey + '_') + 'name'
      variant = getattr(metadefs, defname, None)
      # non-empty string or None
      variant = variant and (str(variant) or None) or None
      variants[variantkey] = variant

    # create final base name (helper) variants
    # (NOT stored in final meta object (`self`))
    key = ''
    name = (
      variants[key]
      or prefixes[key] + decamelize(handlerclsname) + suffixes[key])
    key = 'plural'
    plural_name = (
      variants[key] and prefixes[key] + variants[key] + suffixes[key]
      or None)
    key = 'upper'
    upper_name = (
      variants[key]
      or variants[''] and camelize(variants[''])
      or prefixes[key] + handlerclsname + suffixes[key])
    key = 'plural_upper'
    plural_upper_name = (
      variants[key]
      or variants['plural']
      and prefixes[key] + camelize(variants['plural']) + (
        suffixes[key] or (not variants['plural'] and 's' or ''))
      or None)

    # create final identifier/verbose name variants
    # (stored in final meta object (`self`))
    key = 'identifier'
    self.identifier_name = (
      variants[key]
      or prefixes[key] + name + suffixes[key])
    key = 'plural_identifier'
    self.plural_identifier_name = (
      variants[key]
      or prefixes[key] + (plural_name or name) + (
        suffixes[key] or (not plural_name and 's' or '')))
    key = 'upper_identifier'
    self.upper_identifier_name = (
      variants[key]
      or prefixes[key] + upper_name + suffixes[key])
    key = 'verbose'
    self.verbose_name = (
      variants[key]
      or prefixes[key] + upper_name + suffixes[key])
    key = 'plural_verbose'
    self.plural_verbose_name = (
      variants[key]
      or prefixes[key] + (plural_upper_name or upper_name) + (
        suffixes[key] or (not plural_upper_name and 's' or '')))

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
      meta = Meta(handlerclsname = clsname, metadefs = metadefs)
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
