# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2016 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""robottools.library.session.meta

Provides testlibrary()'s session handler metaclass.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['SessionHandlerMeta']

import inspect
import re
from copy import deepcopy

from moretools import dictitems

from robottools.library.keywords import KeywordsDict
from .metaoptions import Meta


class SessionHandlerMeta(type):
    """The metaclass for :class:`Handler`.

    - For user-derived handler classes
      it generates the handler specific meta information
      (using :class:`.meta.Meta`),
      the session storage, the actual Robot Keywords for session management,
      and a session exception type.
    """
    def __new__(mcs, clsname, bases, clsattrs):
        """Generate meta information, session exception type,
           and session/keywords storage
           for :class:`Handler` derived classes.
        """
        if clsname == 'Handler': # The handler base class itself
            return type.__new__(mcs, clsname, bases, clsattrs)

        try: # Has a user-defined `Handler.Meta` class?
            options = clsattrs['Meta']
        except KeyError:
            meta = Meta(handlerclsname=clsname)
        else:
            meta = Meta(handlerclsname=clsname, options=options)
        clsattrs['meta'] = meta

        excname = meta.upper_identifier_name + 'Error'
        clsattrs['SessionError'] = type(excname, (RuntimeError,), {})

        # The handler's dictionary of opened sessions
        clsattrs['sessions'] = {}
        # The handler's currently active session
        clsattrs['session'] = None

        # For storing the handler's session management Keywords
        clsattrs['keywords'] = KeywordsDict()

        return type.__new__(mcs, clsname, bases, clsattrs)

    #TODO: (cls, name, func) ?
    def add_opener(cls, func, close_func=None):
        """Add Keywords for opening (un)named sessions
           for a user-defined session opener method `func`
           (methods whose names start with 'open').

        - Optional `close_func` will be called on active unnamed sessions
          when opening new sessions.
        """
        suffix = re.sub('^open($|_)', '', func.__name__)
        keywordname = 'open%s_' + cls.meta.identifier_name
        if suffix:
            keywordname += '_' + suffix
        argspec = inspect.getargspec(func)

        def open_session(self, *args, **kwargs):
            """Open an unnamed %s.

            - Automatically closes active unnamed %s.
            """
            previous = cls.session
            active = func(self, *args, **kwargs)
            cls.add_session(active)
            if previous is not None and close_func:
                # explicitly close previously active session if unnamed
                for name, session in dictitems(cls.sessions):
                    if session is previous:
                        break
                else:
                    close_func(self, previous)

        open_session.__doc__ %= (
          cls.meta.verbose_name, cls.meta.plural_verbose_name)

        open_session.argspec = argspec
        # Use custom doc string if defined
        if func.__doc__:
            open_session.__doc__ = func.__doc__
        cls.keywords[keywordname % ''] = open_session

        def open_named_session(self, name, *args, **kwargs):
            """Open a named %s.

            - Automatically closes active unnamed %s.
            """
            previous = cls.session
            active = func(self, *args, **kwargs)
            cls.add_named_session(name, active)
            if previous is not None and close_func:
                # explicitly close previously active session if unnamed
                for name, session in cls.sessions.items():
                    if session is previous:
                        break
                else:
                    close_func(self, previous)

        open_named_session.__doc__ %= (
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
        - Looks for optional custom session switch/close hook methods
          named 'switch'/'close'
        - All Keyword names include the handler-specific
          `meta.identifier_name`.
        """
        try:
            meta = cls.meta
        except AttributeError:
            return

        open_funcs = []
        switch_func = close_func = None
        for name, func in dictitems(clsattrs):
            if name.startswith('open'):
                open_funcs.append(func)
            elif name == 'switch':
                switch_func = func
            elif name == 'close':
                close_func = func
        for func in open_funcs:
            cls.add_opener(func, close_func=close_func)

        def switch_session(self, name):
            previous = cls.session
            active = cls.switch_session(name)
            if previous is not None and close_func:
                # explicitly close previously active session if unnamed
                for name, session in dictitems(cls.sessions):
                    if session is previous:
                        break
                else:
                    close_func(self, previous)
            if switch_func:
                switch_func(self, active)

        keywordname = 'switch_' + meta.identifier_name
        cls.keywords[keywordname] = switch_session

        def close_session(self, name=None):
            session = cls.close_session(name)
            if close_func:
                close_func(self, session)

        keywordname = 'close_' + meta.identifier_name
        cls.keywords[keywordname] = close_session
