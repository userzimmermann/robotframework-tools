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

"""robotshell.magic.keyword

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['KeywordMagic']

from .base import RobotMagicBase


class KeywordMagic(RobotMagicBase):
    def __init__(self, keyword, **baseargs):
        RobotMagicBase.__init__(self, **baseargs)
        self.keyword = keyword

    @property
    def __doc__(self):
        return self.keyword.__doc__

    def __str__(self):
        return self.keyword.name

    def __call__(self, args_str):
        if not args_str:
            args = ()
        elif any(args_str.startswith(c) for c in '[|'):
            args = [s.strip() for s in args_str.strip('[|]').split('|')]
        else:
            args = args_str.split()

        if self.robot_shell.robot_debug_mode:
            return self.keyword.debug(*args)
        return self.keyword(*args)


class KeywordCellMagic(KeywordMagic):
    def __call__(self, options_str, args_str):
        """Call the given with the line-wise given args
           and extra named arguments given as option flags.
        """
        args = filter(None, (
          s.strip() for s in args_str.strip().split('\n')))
        options_str = options_str.strip()
        if not options_str:
            return self.keyword(*args)

        if not options_str.startswith('--'):
            raise ValueError(options_str)
        options = {}
        name = None
        values = []

        def add_option():
            if name:
                options[name] = values and ' '.join(values) or True

        for word in options_str.split():
            if word.startswith('--'):
                add_option()
                values = []
                name = word.strip('-').replace(*'-_')
                if not name:
                    raise ValueError
            else:
                values.append(word)
        add_option()
        return self.keyword(*args, **options)
