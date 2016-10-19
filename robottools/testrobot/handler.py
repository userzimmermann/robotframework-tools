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

"""robottools.testrobot.handler

Making ``robot.running.handlers`` work better with
:class:`robottools.TestRobot`.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['Handler']

from moretools import isstring, dictitems


class Handler(object):
    """A wrapper for instances of classes from ``robot.running.handlers``,
    implementing a custom :meth:`.resolve_arguments`,
    which supports passing arbitrary python objects
    as keyword argument values.
    """
    def __init__(self, handler):
        """Create with the `handler` instance to wrap.
        """
        self._handler = handler

    def __getattr__(self, name):
        return getattr(self._handler, name)

    # HACK
    def resolve_arguments(self, args_and_kwargs, variables):
        """More Pythonic argument handling for interactive
        :class:`robottools.testrobot.keyword.Keyword` calls.

        Original ``resolve_arguments`` methods from ``robot.running.handlers``
        expect as first argument a single list of Keyword arguments
        coming from an RFW script::

           ['arg0', 'arg1', ..., 'name=value', ...]

        So there is no chance to pass unstringified named argument values.
        Only unstringified positional arguments are possible.

        This wrapper method takes a normal Python `args_and_kwargs` pair
        instead as first argument::

           (arg0, arg1, ...), {name: value, ...}

        It resolves the named arguments stringified via the original method
        but returns the original Python values::

           [arg0, arg1, ...], [(name, value), ...]

        Only strings are untouched.
        So RFW ``'...${variable}...'`` substitution still works.
        """
        posargs, kwargs = args_and_kwargs
        rfwargs = list(posargs)
        # prepare 'key=value' strings for original RFW method
        for name, value in dictitems(kwargs):
            if not isstring(value):
                value = repr(value)
            rfwargs.append(u'%s=%s' % (name, value))
        posargs, rfwkwargslist \
            = self._handler.resolve_arguments(rfwargs, variables)
        # and replace values with original non-string objects after resolving
        kwargslist = []
        for name, rfwvalue in rfwkwargslist:
            value = kwargs[name]
            if isstring(value):
                value = rfwvalue
            kwargslist.append(value)
        return posargs, kwargslist
