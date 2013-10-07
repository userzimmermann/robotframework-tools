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

import inspect
import re
from copy import deepcopy

from ..keywords import KeywordsDict

# the session handler meta information management
from .meta import Meta

class HandlerMeta(type):
    """The custom type class for :class:`Handler`.

    - For user-derived handler classes
      it generates the handler specific meta information
      (using :class:`.meta.Meta`),
      the session storage, the actual Robot Keywords for session management,
      and a session exception type.
    """
    def __new__(metacls, clsname, bases, clsattrs):
        """Generate meta information, session exception type,
           and session/keywords storage
           for :class:`Handler` derived classes.
        """
        if clsname == 'Handler': # The handler base class itself
            return type.__new__(metacls, clsname, bases, clsattrs)

        try: # Has a user-defined `Handler.Meta` class?
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

        # For storing the handler's session management Keywords
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
        argspec = inspect.getargspec(func)

        def open_session(self, *args, **kwargs):
            """Open an unnamed %s.

            - Automatically closes active unnamed %s.
            """
            session = func(self, *args, **kwargs)
            cls.add_session(session)

        open_session.func_doc %= (
          cls.meta.verbose_name, cls.meta.plural_verbose_name)

        open_session.argspec = argspec
        # Use custom doc string if defined
        if func.func_doc:
            open_session.func_doc = func.func_doc
        cls.keywords[keywordname % ''] = open_session

        def open_named_session(self, name, *args, **kwargs):
            """Open a named %s.

            - Automatically closes active unnamed %s.
            """
            session = func(self, *args, **kwargs)
            cls.add_named_session(name, session)

        open_named_session.func_doc %= (
          cls.meta.verbose_name, cls.meta.plural_verbose_name)

        named_argspec = deepcopy(argspec)
        named_argspec.args.insert(1, 'name') # (after self)
        open_named_session.argspec = named_argspec
        cls.keywords[keywordname % '_named'] = open_named_session

    def __init__(cls, clsname, bases, clsattrs):
        """Generate the actual session management keywords
           for :class:`Handler` derived classes.

        - Includes the session management helper methods of :class:`Handler`
          and user-defined session opener methods
          (whose names start with 'open').
        - Looks for an optional custom session close hook method named 'close'
        - All Keyword names include the handler-specific
          `meta.identifier_name`.
        """
        try:
            meta = cls.meta
        except AttributeError:
            return

        close_func = None
        for func in clsattrs.values():
            try:
                name = func.func_name
            except AttributeError: # No function object
                pass
            else:
                if name.startswith('open'):
                    cls.add_opener(func)
                if name == 'close':
                    close_func = func

        def switch_session(self, name):
            cls.switch_session(name)

        keywordname = 'switch_' + meta.identifier_name
        cls.keywords[keywordname] = switch_session

        def close_session(self):
            session = cls.close_session()
            if close_func:
                close_func(self, session)

        keywordname = 'close_' + meta.identifier_name
        cls.keywords[keywordname] = close_session

class Handler(object):
    """The base class for custom Robot Test Library session handler types.
    """
    __metaclass__ = HandlerMeta

    @classmethod
    def add_session(cls, session):
        """Helper method for adding an unnamed session to the handler
           and making it active.

        - Automatically closes already running unnamed sessions.
        """
        cls.session = session

    @classmethod
    def add_named_session(cls, name, session):
        """Helper method for adding a named session to the handler
           and making it active.

        - Automatically closes running unnamed sessions.
        """
        name = str(name)
        cls.session = cls.sessions[name] = session

    @classmethod
    def switch_session(cls, name):
        """Helper method for switching the currently active session.

        - Automatically closes running unnamed sessions.
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
        session = cls.session
        cls.session = None
        return session
