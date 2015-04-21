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

"""robotshell.library

Test Library handler with IPython (notebook) features

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['TestLibrary']

from six.moves.urllib_parse import quote as urlquote

import robottools.testrobot
from robottools import libdoc


class TestLibrary(robottools.testrobot.TestLibrary):
    def _repr_html_(self):
        html = libdoc.html(self.name)
        return """
          <iframe width="100%%" height="100%%" frameborder="0"
                  src="data:text/html;charset=utf-8,%s"
                  > """ % urlquote(html) + """
          </iframe>
          """
