# robotframework-tools
#
# Python Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013-2014 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""robottools.setup

Python Tools for Robot Framework and Test Libraries.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
import os


PROJECT = 'robotframework-tools'

try:
    from path import path as Path
    with Path(__file__).abspath().dirname():
        exec(open('zetup.py'))
except (ImportError, NameError): # No path or __file__
    exec(open('zetup.py'))


REQUIRES += (
  'robotframework >= 2.8' if sys.version_info[0] == 2
  else 'robotframework-python3 >= 2.8.4'
  )
