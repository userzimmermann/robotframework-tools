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

"""robotshell.result

Test run result wrapper with IPython (notebook) features.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestResult']

from six.moves.urllib_parse import quote as urlquote

import robottools


class TestResult(robottools.TestResult):
    """robotshell wrapper interface for robot test run results.

    - Instances are returned from %Run magic.
    - Automatically displays tabbed log and report HTML
      in resizable <iframe> boxes in IPython notebook.
    """
    def _repr_html_(self):
        """The tabbed log and report HTML code
           to be displayed as notebook cell output.
        """
        return """
          <div class="robotshell-test-result">
            <ul>
              <li><a href="#robotshell-test-result-tab-log">Log</a>
              </li>
              <li><a href="#robotshell-test-result-tab-report">Report</a>
              </li>
            </ul>
            <div id="robotshell-test-result-tab-log"
                 class="robotshell-test-result-tab"
                 >
              <iframe width="100%%" height="100%%" frameborder="0"
                      src="data:text/html;charset=utf-8,%s"
                      > """ % urlquote(self.log_html) + """
              </iframe>
            </div>
            <div id="robotshell-test-result-tab-report"
                 class="robotshell-test-result-tab"
                 >
              <iframe width="100%%" height="100%%" frameborder="0"
                      src="data:text/html;charset=utf-8,%s"
                      > """ % urlquote(self.report_html) + """
              </iframe>
            </div>
          </div>
          <script type="text/javascript">
            $("div.robotshell-test-result").tabs();
            $("div.robotshell-test-result-tab").resizable({
              autoHide: true,
              handles: "s"
            });
          </script>
          """
