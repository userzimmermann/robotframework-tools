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

"""robottools.testrobot.highlighting

A thin wrapper module for `robot.output.highlighting`.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Highlighter']

try: # Robot 2.9
    from robot.output.console.highlighting import Highlighter as _Highlighter
except ImportError:
    from robot.output.highlighting import Highlighter as _Highlighter


class Highlighter(object):
    def __init__(self, color, stream):
        self.color = color
        self.stream = stream
        self._highlighter = _Highlighter(stream)

    def __enter__(self):
        getattr(self._highlighter, self.color)()
        return self.stream

    def __exit__(self, *exc):
        self._highlighter.reset()
