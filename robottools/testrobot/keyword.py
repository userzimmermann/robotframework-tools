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

"""robottools.testrobot.keyword

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Keyword']

import sys
from six import reraise, text_type as unicode

from robot.errors import HandlerExecutionFailed, ExecutionFailed
import robot.running
try: # Robot 3.0
    from robot.running.steprunner import StepRunner
    from robot.running.statusreporter import StatusReporter
except ImportError:
    StatusReporter = None
else:
    _get_failure = StatusReporter._get_failure
try: # Robot 2.9
    from robot.running.keywordrunner import NormalRunner
except ImportError:
    NormalRunner = None

from robottools.library.inspector.keyword import KeywordInspector

from .handler import Handler


def debug_fail(context, exc_info=None):
    """Handles a Keyword FAIL in debugging mode
       by writing some extra output to the given Robot `context`
       and re-raising the exception that caused the FAIL.
    """
    # Get the Exception raised by the Keyword
    exc_type, exc, traceback = exc_info or sys.exc_info()
    context.output.fail("%s: %s" % (exc_type.__name__, exc))
    context.output.debug("Re-raising exception...")
    # Search the oldest traceback frame of the actual Keyword code
    # (Adapted from robot.utils.error.PythonErrorDetails._get_traceback)
    while traceback:
        try:
            modulename = traceback.tb_frame.f_globals['__name__']
        except KeyError:
            break
        if modulename.startswith('robot.running.'):
            traceback = traceback.tb_next
        else:
            break
    reraise(exc_type, exc, traceback)


if NormalRunner: # Robot 2.9
    #HACK
    class DebugNormalRunner(NormalRunner):
        """On-demand-replacement (monkey patch)
        for :class:`robot.runnning.keywordrunner.NormalRunner`
        to catch the exception that caused a Keyword FAIL for debugging.
        """
        def _get_and_report_failure(self):
            debug_fail(self._context)


if StatusReporter: # Robot 3.0
    #HACK
    def debug_get_failure(self, exc_type, exc, traceback, context):
        """On-demand-replacement (monkey patch) for
        :meth:`robot.running.statusreporter.StatusReporter._get_failure`
        to catch the exception that caused a Keyword FAIL for debugging.
        """
        if exc is None:
            return None

        debug_fail(context, (exc_type, exc, traceback))


class DebugKeyword(robot.running.Keyword):
    """Derived :class:`robot.running.Keyword` runner
       that catches the exception that caused a Keyword FAIL
       for debugging.
    """

    # Robot 2.8
    def _report_failure(self, context):
        debug_fail(context)

    # Robot >= 2.9
    def __enter__(self):
        if NormalRunner:
            # Robot 2.9
            # HACK: monkey-patch robot.running's NormalRunner
            # to catch the Keyword exception
            robot.running.keywordrunner.NormalRunner = DebugNormalRunner
        if StatusReporter:
            # Robot 3.0
            # HACK: monkey-patch robot.running's StatusReporter._get_failure()
            # to catch the Keyword exception
            robot.running.statusreporter.StatusReporter._get_failure \
                = debug_get_failure

    def __exit__(self, *exc):
        if NormalRunner:
            robot.running.keywordrunner.NormalRunner = NormalRunner
        if StatusReporter:
            robot.running.statusreporter.StatusReporter._get_failure \
                = _get_failure


class Keyword(KeywordInspector):
    def __init__(self, handler, context, debug=False):
        KeywordInspector.__init__(self, handler)
        if not isinstance(handler, Handler):
            handler.__class__ = Handler[handler.__class__]
        self._context = context
        self._debug = debug

    @property
    def __doc__(self):
        return KeywordInspector.__doc__.fget(self)

    def __call__(self, *args, **kwargs):
        # HACK: normally, RFW's Keyword argument resolvers expect
        # a plain list of arguments coming from an RFW script,
        # which has limitations, as described in the .handler.Handler wrapper,
        # which is patched later into the actual Keyword function runner
        # by self._context.get_runner(),
        # and which expects the (args, kwargs) pair instead
        if self._debug:
            runner = DebugKeyword(self.name, args=(args, kwargs))
        else:
            runner = robot.running.Keyword(self.name, args=(args, kwargs))
        # HACK: `with` registers Context to EXECUTION_CONTEXTS
        # and Output to LOGGER:
        with self._context as ctx:
            try:
                # Robot >= 2.9
                if (StatusReporter or NormalRunner) and isinstance(
                        runner, DebugKeyword
                ):
                    with runner:
                        return runner.run(ctx)

                return runner.run(ctx)
            # Robot 2.8: raised by robot.running.Keyword:
            except HandlerExecutionFailed:
                pass

    def debug(self, *args, **kwargs):
        keyword = Keyword(self._handler, self._context, debug=True)
        return keyword(*args, **kwargs)
