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

from IPython.display import HTML

import robottools


class TestResult(robottools.TestResult, HTML):
    """robotshell wrapper interface for robot test run results.

    - Instances are returned from %Run magic.
    - Automatically displays the log HTML in a resizable <iframe>
      in IPython notebook.
    """
    @property
    def data(self):
        """The HTML code to be displayed as cell output.

        - Required by :class:`IPython.display.HTML`
          (as dynamic alternative to passing data to HTML.__init__)
        """
        return """
          <div class="robotshell-test-result">
            <iframe width="100%%" height="100%%" frameborder="0"
                    src="data:text/html;charset=utf-8,%s"
                    > """ % urlquote(self.log_html) + """
            </iframe>
          </div>
          <script type="text/javascript">
            $("div.robotshell-test-result").resizable({
              autoHide: true,
              handles: "s"
            });
          </script>
          """
