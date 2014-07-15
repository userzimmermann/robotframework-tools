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

"""robottools

Python Tools for Robot Framework and Test Libraries.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

from robottools import zetup

__version__ = zetup.VERSION

__requires__ = zetup.REQUIRES.checked
__extras__ = zetup.EXTRAS

__distribution__ = zetup.DISTRIBUTION.find(__path__[0])


from robottools.library import *
from robottools.library.keywords import *
from robottools.library.session import SessionHandler
from robottools.library.context import *

from robottools.library.inspector import *

from robottools.testrobot import *
