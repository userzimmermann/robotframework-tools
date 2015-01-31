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

"""robottools.remote.keywords

Defines extra Keywords for RemoteRobot.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

from . import TestLibrary


keyword = TestLibrary.keyword


@keyword
def import_remote_library(self, name):
    """Remotely import the Test Library with given `name`.

    Does the same remotely as `BuiltIn.Import Library` does locally.
    The Test Library must be allowed on server side.

    The `Remote` client library must be reloaded
    to make the new Keywords accessible.
    This can be done with `ToolsLibrary.Reload Library`.
    """
    if name not in self.allow_import:
        raise RuntimeError(
          "Importing Remote Library '%s' is not allowed." % name)
    lib = self.Import(name)
    if self.register_keywords:
        self._register_keywords(lib)
