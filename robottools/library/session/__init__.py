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

"""robottools.library.session

testlibrary()'s session handler framework.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass

__all__ = ['SessionHandler']

from .meta import SessionHandlerMeta


class SessionHandler(with_metaclass(SessionHandlerMeta, object)):
    """The base class for custom Robot Test Library session handler types.
    """

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
            session = cls.session = cls.sessions[name]
        except KeyError:
            raise cls.SessionError('Session not found: %s' % repr(name))
        return session

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


# For backwards compatibility:
Handler = SessionHandler
