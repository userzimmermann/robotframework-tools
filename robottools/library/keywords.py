# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""robottools.keywords

Provides a `moretools.simpledict` mapping type
for storing Robot Test Library Keyword methods,
provding dynamic Test-Case-like CamelCase access for interactive use.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = 'KeywordsDict',

import re

from moretools import simpledict, camelize, decamelize

# A mapping type for storing Robot Library Keyword methods by name,
# providing additional `__getattr__` access with CamelCase Keyword names
KeywordsDict = simpledict(
  'Keywords',
  # convert lower_case keyword names to CamelCase attribute names
  key_to_attr = camelize,
  # convert CamelCase keyword attribute names back to lower_case
  attr_to_key = decamelize)
