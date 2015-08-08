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

"""robottools.testrobot.output

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Output']

import re
import sys
import logging

from robot.output import LOGGER, LEVELS as LOG_LEVELS
from robot.output.loggerhelper import AbstractLogger
from robot.output.pyloggingconf import RobotHandler

from .highlighting import Highlighter


LOG_LEVELS_MAX_WIDTH = max(map(len, LOG_LEVELS))


LOG_LEVEL_COLORS = {
  'FAIL': 'red',
  'ERROR': 'red',
  'WARN': 'yellow',
  }


class LoggingHandler(RobotHandler):
    def __enter__(self):
        #HACK: Adapted from robot.output.pyloggingconf.initialize()
        self._old_logging_raiseExceptions = logging.raiseExceptions
        logging.raiseExceptions = False
        logging.getLogger().addHandler(self)

    def __exit__(self, *exc):
        logging.getLogger().removeHandler(self)
        logging.raiseExceptions = self._old_logging_raiseExceptions
        del self._old_logging_raiseExceptions


class Output(AbstractLogger):
    def __init__(self, log_level='INFO'):
        AbstractLogger.__init__(self, level=log_level)
        self.logging_handler = LoggingHandler()
        # streams to be used internally for writing messages
        # - see self.__enter__() and self.message()
        self._out = self._err = None

    def set_log_level(self, level):
        return self.set_level(level)

    def __enter__(self):
        # save sys.stdout and sys.stderr for writing
        self._out = sys.stdout
        self._err = sys.stderr
        #HACK: Dynamically (un)register Output:
        LOGGER.disable_message_cache()
        LOGGER.unregister_console_logger()
        LOGGER.register_logger(self)
        # Catch global logging:
        self.logging_handler.__enter__()

    def __exit__(self, *exc):
        #HACK:
        self.logging_handler.__exit__(*exc)
        LOGGER.unregister_logger(self)
        # unset internal streams
        self._out = self._err = None

    _re_log_level = re.compile('|'.join(r % '|'.join(LOG_LEVELS)
      for r in [r'^\[ ?(%s) ?\] *', r'^\* ?(%s) ?\* *']))

    def message(self, message):
        msg = message.message
        try:
            _, brackets, stars, msg = self._re_log_level.split(msg)
        except ValueError:
            level = message.level
        else:
            level = brackets or stars
        if not self._is_logged(level):
            return

        # select streams to use
        if level == 'INFO':
            stream = self._out or sys.__stdout__
        else:
            stream = self._err or sys.__stderr__
        #... and finally write the message
        stream.write("[ ")
        try:
            color = LOG_LEVEL_COLORS[level]
        except KeyError:
            stream.write(level)
        else:
            with Highlighter(color, stream) as hl:
                hl.write(level)
        stream.write(" ]%s %s\n" % (
          ' ' * (LOG_LEVELS_MAX_WIDTH - len(level)), msg))

    def fail(self, message, *args):
        self._last_fail_exc = sys.exc_info()
        AbstractLogger.fail(self, message, *args)

    def register_error_listener(self, listener):
        pass

    def start_suite(self, suite):
        pass

    def end_suite(self, suite):
        pass

    def start_test(self, test):
        pass

    def end_test(self, test):
        pass

    def start_keyword(self, kw):
        pass

    def end_keyword(self, kw):
        pass
