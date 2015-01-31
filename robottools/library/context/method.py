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

"""robottools.context.method

Provides :class:`contextmethod` for creating `testlibrary` method decorators
to separate method implementations for different contexts
of :class:`ContextHandler`s.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['contextmethod']

from moretools import Lazy, LazyDict


class contextmethod(object):
    """Class for creating `testlibrary` method decorators
       to separate method implementations for different contexts
       of :class:`ContextHandler`s.

    - Decorated methods get Context name attributes for decorating
      the Context specific method implementations::

       @contextmethod(Handler)
       def method(self, ...):
           pass

       @method.<context name>
       def context_method(self, ...):
           ...

    - By default, on method call only the implementation
      matching the currently active Context will be called.

    - A @contextmethod.combined(Handler) decorated method
      will call all context specific implementations
      and return a `dict` containing the results by Context name keys.
    - contextmethod.combined decorated methods will get an additional
      .result decorator for defining a hook method
      processing the results dict before final return::

       @method.result
       def result_method(self, results_dict):
           ...
           return results_dict # or whatever...

    - A @contextmethod.combined.lazy(Handler) decorated method
      will return a :class:`LazyDict` which will call
      the context specific implementations on first ['<context name>'] access.
    """
    def __init__(self, *handlers, **options):
        """Create a decorator for the given `handlers`.

        - Currently only 1 Handler supported :( - will change soon :)
        - `options` are implicitly given
          by derived :class:`combined` and :class:`lazy`.
        """
        self.handlers = handlers
        self.combined = options.pop('combined', False)
        self.lazy = options.pop('lazy', False)

    def __call__(self, func):
        """The actual decoration logic.
        """
        handlers = self.handlers
        combined = self.combined
        lazy = self.lazy
        # To collect the context specific method implementations
        # decorated with @method.<context name>:
        ctxfuncs = {}

        # The wrapper method returned by this decorator
        def method(self, *args, **kwargs):
            # First call the decorated main func as prerequisite:
            func(self, *args, **kwargs)
            if combined:
                if lazy:
                    results = LazyDict()
                    for context, ctxfunc in ctxfuncs.items():
                        results[context.name] = Lazy(
                          ctxfunc, self, *args, **kwargs)
                else:
                    results = {}
                    for context, ctxfunc in ctxfuncs.items():
                        results[context.name] = ctxfunc(
                          self, *args, **kwargs)
                # Check if .result decorator was used
                # to define a custom hook method:
                if method.result is not resultdeco:
                    results = method.result(self, results)
                return results
            # Default behavior (only call 1 method implementation):
            for context in self.contexts:
                if context.handler in handlers:
                    break
            else:
                #TODO
                raise RuntimeError
            ctxfunc = ctxfuncs[context]
            return ctxfunc(self, *args, **kwargs)

        # Create method.<context name> decorators:
        for handler in handlers:
            for context in handler.contexts:
                def ctxdeco(ctxfunc, _context=context):
                    ctxfuncs[_context] = ctxfunc
                    return ctxfunc

                setattr(method, context.name, ctxdeco)

        def resultdeco(resultfunc):
            method.result = resultfunc
            return resultfunc

        method.result = resultdeco

        method.__name__ = func.__name__
        return method


class combined(contextmethod):
    def __init__(self, *handlers, **options):
        contextmethod.__init__(self, *handlers, combined=True, **options)


class lazy(combined):
    def __init__(self, *handlers):
        combined.__init__(self, *handlers, lazy=True)


combined.lazy = lazy
contextmethod.combined = combined
