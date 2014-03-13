# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
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

"""robottools.context.method

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['contextmethod']


class contextmethod(object):
    def __init__(self, *handlers):
        self.handlers = handlers

    def __call__(self, func):
        handlers = self.handlers
        ctxfuncs = {}

        def method(self, *args, **kwargs):
            for context in self.contexts:
                if context.handler in handlers:
                    break
            else:
                #TODO
                raise RuntimeError
            ctxfunc = ctxfuncs[context]
            return ctxfunc(self, *args, **kwargs)

        for handler in handlers:
            for context in handler.contexts:
                def ctxdeco(ctxfunc, _context=context):
                    ctxfuncs[_context] = ctxfunc
                    return method

                setattr(method, context.name, ctxdeco)

        method.__name__ = func.__name__
        return method
