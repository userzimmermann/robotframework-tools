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

"""robottools.context

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass

__all__ = [
  'ContextHandler',
  # From .method:
  'contextmethod']

from robottools.library.session.metaoptions import Meta
from robottools.library.keywords import KeywordsDict

from .method import *


class Context(object):
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

    def __call__(self, func):
        try:
            func.contexts.add(self)
        except AttributeError:
            func.contexts = set([self])
        return func

    def __repr__(self):
        return "%s.%s" % (self.handler.__name__, self.name)


class ContextHandlerMeta(type):
    ## def __new__(metacls, clsname, bases, clsattrs):
    ##     if clsname == 'ContextHandler': # The handler base class itself
    ##         return type.__new__(metacls, clsname, bases, clsattrs)

    ##     try: # Has a user-defined `Handler.Meta` class?
    ##         metadefs = clsattrs['Meta']
    ##     except KeyError:
    ##         meta = Meta(handlerclsname = clsname)
    ##     else:
    ##         meta = Meta(handlerclsname = clsname, metadefs = metadefs)
    ##     clsattrs['meta'] = meta

    ##     return type.__new__(metacls, clsname, bases, clsattrs)

    def __init__(cls, clsname, bases, clsattrs):
        try:
            names = cls.contexts
        except AttributeError:
            return
        cls.contexts = []
        for name in names:
            context = Context(name, handler=cls)
            cls.contexts.append(context)
            setattr(cls, name, context)

        cls.keywords = KeywordsDict()

        # Look for a custom switch hook method:
        switch_func = clsattrs.get('switch')

        def switch_context(self, name):
            for current in self.contexts:
                if current.handler is cls:
                    break
            for context in cls.contexts:
                if context.name == name:
                    self.contexts.remove(current)
                    self.contexts.append(context)
                    if switch_func: # Custom switch hook
                        switch_func(self, name)
                    return
            raise ValueError(name)

        keyword_name = switch_context.__name__ = 'switch_' + clsname.lower()
        cls.keywords[keyword_name] = switch_context


class ContextHandler(with_metaclass(ContextHandlerMeta, object)):
    def __init__(self):
        try:
            default = type(self).default
        except AttributeError:
            self.default = self.contexts[0]
        else:
            self.default = self[default]

    def __getitem__(self, name):
        for context in self.contexts:
            if context.name == name:
                return context
        raise KeyError(name)
