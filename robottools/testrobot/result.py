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

"""robottools.testrobot.result

Test run result wrapper for :class:`robottools.TestRobot`.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestResult']

from io import StringIO

from robot.conf import RobotSettings
from robot.reporting import ResultWriter
from robot.reporting.resultwriter import Results


class Buffer(StringIO):
    """Byte stream buffer class to be used for getting data
       from :class:`robot.reporting.ResultWriter` interfaces.

    - ResultWriter normally expects file paths or file streams
      and closes them after writing data to them.
    """
    def close(self):
        """Dummy method to prevent the buffer from getting closed.
        """
        pass


class TestResult(object):
    """robotshell wrapper interface for robot test run results.
    """
    def __init__(self, result):
        """Initialize with a :class:`robot.result.Result` instance.
        """
        self.robot_result = result

    @property
    def writer(self):
        """Return a :class:`robot.reporting.ResultWriter` interface
           for the wrapped test run result,
           which can generate output/log/report data.
        """
        return ResultWriter(self.robot_result)

    @property
    def output_xml(self):
        """Return the test run result as XML data (byte string),
           like it gets written to output.xml files by robot.
        """
        xml = Buffer()
        self.writer._write_output(self.result, xml)
        xml.seek(0)
        return xml.read()

    @property
    def log_html(self):
        """Return the test run log as HTML data (byte string),
           like it gets written to log.html files by robot.
        """
        html = Buffer()
        self.writer._write_log(
          Results(RobotSettings(), self.robot_result).js_result,
          html, {})
        html.seek(0)
        return html.read()
