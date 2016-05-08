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

"""robottools

Python Tools for Robot Framework and Test Libraries.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

from zetup import find_zetup_config
from zetup.version import Version

zfg = find_zetup_config(__name__)

__distribution__ = zfg.DISTRIBUTION.find(__path__[0])
__description__ = zfg.DESCRIPTION

__version__ = zfg.VERSION

__requires__ = zfg.REQUIRES.checked
__extras__ = zfg.EXTRAS

## __notebook__ = zfg.NOTEBOOKS['README']

try:
    import robot
except ImportError as exc:
    raise ImportError(
        "%s depends on robotframework but import failed with: %s"
        % (repr(__distribution__), exc))
if Version(robot.__version__) < '2.8.7':
    raise __import__('pkg_resources').VersionConflict(
        "%s needs robotframework>=2.8.7 but found %s in %s"
        % (repr(__distribution__), robot.__version__, repr(robot)))

from robottools.library import *
from robottools.library.keywords import *
from robottools.library.session import SessionHandler
from robottools.library.context import *

from robottools.library.inspector import *
from robottools.libdoc import libdoc

from robottools.testrobot import *

from .utils import *
