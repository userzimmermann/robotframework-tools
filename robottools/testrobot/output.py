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
from robot.output.highlighting import Highlighter

from .highlighting import Highlighter


LOG_LEVELS_MAX_WIDTH = max(map(len, LOG_LEVELS))

#HACK: To dynamically (un)register `Output`s:
LOGGER.disable_message_cache()
LOGGER.disable_automatic_console_logger()

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
        self.stream = sys.__stdout__

    def set_log_level(self, level):
        return self.set_level(level)

    def __enter__(self):
        #HACK:
        LOGGER.register_logger(self)
        # Catch global logging:
        self.logging_handler.__enter__()

    def __exit__(self, *exc):
        #HACK:
        self.logging_handler.__exit__(*exc)
        LOGGER.unregister_logger(self)

    _re_msg_label = re.compile(r'^\[(%s)\] *' % '|'.join(LOG_LEVELS))

    def message(self, message):
        msg = message.message
        try:
            _, level, msg = self._re_msg_label.split(msg)
        except ValueError:
            level = message.level
        if not self._is_logged(level):
            return
        self.stream.write("[")
        try:
            color = LOG_LEVEL_COLORS[level]
        except KeyError:
            self.stream.write(level)
        else:
            with Highlighter(color, self.stream) as stream:
                stream.write(level)
        self.stream.write("]%s %s\n" % (
          ' ' * (LOG_LEVELS_MAX_WIDTH - len(level)), msg))
