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

"""robottools.testrobot

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestRobot']

import sys
import warnings

from moretools import isidentifier

from robot.errors import DataError, HandlerExecutionFailed
## from robot.utils.error import ErrorDetails, PythonErrorDetails
from robot.conf import RobotSettings
from robot.variables import GLOBAL_VARIABLES, init_global_variables
from robot.output.loggerhelper import LEVELS as LOG_LEVELS, AbstractLogger
from robot.running import EXECUTION_CONTEXTS
import robot.running

from robottools.library.inspector import (
  TestLibraryInspector, KeywordInspector)

init_global_variables(RobotSettings())

LOG_LEVELS_MAX_WIDTH = max(map(len, LOG_LEVELS))

class Output(AbstractLogger):
    def message(self, message):
        level = message.level
        print('[%s]%s %s' % (
          message.level, ' ' * (LOG_LEVELS_MAX_WIDTH - len(level)),
          message.message))

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
        raise exc_type, exc_value, traceback

class TestLibrary(TestLibraryInspector):
    def __init__(self, lib, context):
        TestLibraryInspector.__init__(self, lib)
        self._context = context

    def __getattr__(self, name):
        keyword = TestLibraryInspector.__getattr__(self, name)
        return Keyword(keyword._handler, self._context)

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
        #HACK: For the Robot BuiltIn Library
        EXECUTION_CONTEXTS._contexts = [self._context]
        try:
            return runner.run(self._context)
        # Raised by robot.running.Keyword:
        except HandlerExecutionFailed as e:
            pass
        #HACK:
        EXECUTION_CONTEXTS._contexts = []

    def debug(self, *args, **kwargs):
        keyword = Keyword(self._handler, self._context, debug=True)
        return keyword(*args, **kwargs)

class Context(object):
    def __init__(self, testrobot):
        self.testrobot = testrobot

        self.output = Output()
        self.dry_run = False
        self.in_teardown = False
        self.test = None

    @property
    def variables(self):
        return self.testrobot._variables

    @property
    def keywords(self):
        return []

    def get_handler(self, name):
        try:
            keyword = self.testrobot[name]
            if type(keyword) is not Keyword:
                raise KeyError(name)
        except KeyError:
            raise DataError(name)
        return keyword._handler

    def start_keyword(self, keyword):
        pass

    def end_keyword(self, keyword):
        pass

    def warn(self, msg):
        self.output.warn(msg)

    def trace(self, msg):
        self.output.trace(msg)

class TestRobot(object):
    def __init__(self, name):
        self.name = name
        self._variables = GLOBAL_VARIABLES.copy()
        self._context = Context(testrobot=self)
        self._libraries = {}

    @property
    def __doc__(self):
        return '%s\n\n%s' % (repr(self), '\n\n'.join(sorted(
          '* [Import] ' + lib.name
          for alias, lib in self._libraries.items())))

    def Import(self, lib, alias=None):
        if type(lib) is not TestLibraryInspector:
            lib = TestLibraryInspector(lib)
        self._libraries[alias or lib.name] = lib
        return lib

    def __getitem__(self, name):
        if name.startswith('$'):
            try:
                return self._variables[name]
            except DataError as e:
                raise KeyError(str(e))
        for alias, lib in self._libraries.items():
            if alias == name:
                return TestLibrary(lib._library, self._context)
            try:
                keyword = lib[name]
            except KeyError:
                pass
            else:
                return Keyword(keyword._handler, self._context)
        raise KeyError(name)

    def __getattr__(self, name):
        if name.isupper(): # Use as variable name
            name = '${%s}' % name
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(str(e))

    def __dir__(self):
        names = []
        for name in self._variables:
            name = name[2:-1] # Strip ${}
            if isidentifier(name):
                names.append(name.upper())
        for alias, lib in self._libraries:
            names.append(alias)
            # dir() returns the Library's CamelCase Keyword names
            names.extend(dir(lib))
        return names

    def __str__(self):
        return self.name

    def __repr__(self):
        return '[Robot] %s' % self
