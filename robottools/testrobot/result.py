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
from six import PY3

__all__ = ['TestResult']

if PY3:
    from io import StringIO
else:
    from io import BytesIO as StringIO

from moretools import isstring

from robot.conf import RebotSettings
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
    def __init__(self, result, **options):
        """Initialize with a :class:`robot.result.Result` instance
           and test run `options`.

        - Writes out 'output' XML, 'log' HTML and 'report' HTML
          if destination streams or file paths are defined in `options`
          (given streams won't get flushed or closed).
        """
        self.robot_result = result
        self.options = options
        # post-processed RebotSettings from **options
        settings = self.settings
        # write output if destinations defined
        for output, format in [
          ('output', 'xml'),
          ('log', 'html'),
          ('report', 'html'),
          ]:
            # first check if output paths or streams are defined in **options
            # because RebotSettings always define default output paths
            file = options.get(output) and getattr(settings, output)
            if not file:
                continue
            # get data from related property
            data = getattr(self, '%s_%s' % (output, format))
            if isstring(file): # file path?
                with open(file, 'w') as f:
                    f.write(data)
            else: # stream
                file.write(data)

    @property
    def settings(self):
        """Get options as post-processed RebotSettings for output generation.
        """
        settings = RebotSettings(**self.options)
        return settings

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

        - Adapted from :meth:`robot.reporting.ReportWriter.write_results`
        """
        xml = Buffer()
        self.writer._write_output(self.robot_result, xml)
        xml.seek(0)
        return xml.read()

    @property
    def log_html(self):
        """Return the test run log as HTML data (byte string),
           like it gets written to log.html files by robot.

        - Adapted from :meth:`robot.reporting.ReportWriter.write_results`
        """
        settings = self.settings
        log_config = settings.log_config
        del log_config['reportURL']
        html = Buffer()
        self.writer._write_log(
          Results(self.settings, self.robot_result).js_result,
          html, log_config)
        html.seek(0)
        return html.read()

    @property
    def report_html(self):
        """Return the test run log as HTML data (byte string),
           like it gets written to log.html files by robot.

        - Adapted from :meth:`robot.reporting.ReportWriter.write_results`
        """
        settings = self.settings
        report_config = settings.report_config
        del report_config['logURL']
        html = Buffer()
        self.writer._write_report(
          Results(settings, self.robot_result).js_result,
          html, report_config)
        html.seek(0)
        return html.read()
