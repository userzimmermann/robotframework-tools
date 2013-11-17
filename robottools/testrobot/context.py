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

"""robottools.testrobot.context

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Context']

from robot.errors import DataError
from robot.running import EXECUTION_CONTEXTS

from .keyword import Keyword


class Context(object):
    def __init__(self, testrobot):
        self.testrobot = testrobot
        self.dry_run = False
        self.in_teardown = False
        self.test = None

    def __enter__(self):
        #HACK: For the Robot BuiltIn Library
        EXECUTION_CONTEXTS._contexts = [self]
        #HACK: Registers output to LOGGER
        self.output.__enter__()
        return self

    def __exit__(self, *exc):
        #HACK: Unregisters output from LOGGER
        self.output.__exit__(*exc)
        #HACK:
        EXECUTION_CONTEXTS._contexts = []

    @property
    def variables(self):
        return self.testrobot._variables

    @property
    def output(self):
        return self.testrobot._output

    @property
    def namespace(self):
        return self.testrobot._namespace

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
