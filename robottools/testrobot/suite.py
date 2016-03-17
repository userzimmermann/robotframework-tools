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

"""robottools.testrobot.suite

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

# from textwrap import indent, dedent
from textwrap import dedent
import tempfile

from path import Path
import modeled

from robot.running import TestSuiteBuilder
import robot.running.model

indent = str


class Suite(modeled.object):

    def __init__(self, testrobot, name):
        self.testrobot = testrobot
        self.rfwsuite = robot.running.model.TestSuite(name=name)

    def Run(self, **options):
        self.testrobot._run(self.rfwsuite, **options)

    def Test(self, name, script=None):
        return Test(self, name, script=script)


class Test(modeled.object):

    def __init__(self, suite, name, script=None):
        self.suite = suite
        self.rfwtest = robot.running.model.TestCase(name=name)
        self.script = script

    @property
    def script(self):
        return self.__dict__['script']

    @script.setter
    def script(self, text):
        # if text is None:
        #     self.rfwtest = robot.running.model.TestCase(name=name)
        #     return
        try:
            fd, fname = tempfile.mkstemp(suffix='.robot', text=True)
            with open(fd, 'w') as f:
                f.write(dedent(
                    """
                    *** Test Cases ***
                    %s
                    %s
                    """) % (self.rfwtest.name, indent(text or "", "    ")))
            tempsuite = TestSuiteBuilder().build(fname)
        finally:
            Path(fname).remove()
        self.rfwtest = test = tempsuite.tests[0]
        tests = self.suite.rfwsuite.tests
        try:
            index = tests.index(self.rfwtest)
        except ValueError:
            tests.append(test)
        else:
            tests[index] = test
        self.__dict__['script'] = text
