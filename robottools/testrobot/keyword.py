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

"""robottools.testrobot.keyword

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Keyword']

import sys
import warnings
import logging

from moretools import isidentifier

from robot.errors import HandlerExecutionFailed
import robot.running

from robottools.library.inspector.keyword import KeywordInspector


class DebugKeyword(robot.running.Keyword):

    def _report_failure(self, context):
        # Get the Exception raised by the Keyword
        exc_type, exc_value, traceback = sys.exc_info()
        context.output.fail("%s: %s" % (exc_type.__name__, exc_value))
        context.output.debug("Re-raising exception...")
        # Search the oldest traceback frame of the actual Keyword code
        # (Adapted from robot.utils.error.PythonErrorDetails._get_traceback)
        while traceback:
            modulename = traceback.tb_frame.f_globals['__name__']
            if modulename.startswith('robot.running.'):
                traceback = traceback.tb_next
            else:
                break
        raise exc_value, None, traceback


class Keyword(KeywordInspector):
    def __init__(self, handler, context, debug=False):
        KeywordInspector.__init__(self, handler)
        self._context = context
        self._debug = debug

    @property
    def __doc__(self):
        return KeywordInspector.__doc__.fget(self)

    def __call__(self, *args, **kwargs):
        args = list(map(str, args))
        args.extend('%s=%s' % item for item in kwargs.items())
        if self._debug:
            runner = DebugKeyword(self.name, args)
        else:
            runner = robot.running.Keyword(self.name, args)
        #HACK: `with` registers Context to EXECUTION_CONTEXTS
        # and Output to LOGGER:
        with self._context as ctx:
            try:
                return runner.run(ctx)
            # Raised by robot.running.Keyword:
            except HandlerExecutionFailed as e:
                pass

    def debug(self, *args, **kwargs):
        keyword = Keyword(self._handler, self._context, debug=True)
        return keyword(*args, **kwargs)
