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

"""robottools.library.libdoc

robot.libdoc alternative with more features.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import PY3

__all__ = ['libdoc']

if PY3: # always need `str` stream
    from io import StringIO
else:
    from StringIO import StringIO

from path import Path
from moretools import isstring

from robot.libdocpkg import LibraryDocumentation
from robot.libdocpkg.writer import LibdocWriter

from .html import HTML


FORMATS = ['xml', 'html']


def libdoc(library, out=None, name=None, version=None, format=None,
           docformat=None, **options):
    """Alternative to :func:`robot.libdoc` with the following extra features:

    - `out` can be a file path (with implicit format from extension)
      or a stream object (which won't be flushed or closed).
      In both cases, the number of written characters will be returned.
    - If `out` is ``None``, the document text will be returned.
    - For 'html' format, some extra post-processing `options` are supported:

      - If ``standalone=False``, the ``<html>``, ``<head>``, ``<meta>``,
        and ``<body>`` tags will be stripped to make the document embeddable
        in existing HTML documents without the use of ``<iframe>``s
      - ``heading=`` can be set to an alternative main heading text
        (which defaults to the library name)
        or to ``False`` to completely remove the heading element.
    """
    outpath = isstring(out) and Path(out)
    if outpath and not format:
        # get implicit format from file extension
        _, ext = Path(out).splitext()
        format = ext[1:] # remove leading '.'
    if not format:
        raise ValueError("Missing format for robottools.libdoc()")
    if format not in FORMATS:
        raise ValueError(
          "Invalid robottools.libdoc() format: %s" % repr(format))
    if format != 'html' and options:
        raise RuntimeError(
          "robottools.libdoc() doesn't support extra options for %s format."
          % repr(format))

    if out is not None:
        class Stream(object):
            """Simple out stream wrapper for counting written characters
               and preventing stream closing.
            """
            count = 0
            # look like a text stream
            encoding = 'utf8'

            def write(self, text):
                self.count += len(text)
                out.write(text)

            def close(self):
                pass

    else: # memory stream for returning text
        class Stream(StringIO):
            """StringIO with close prevention.
            """
            def close(self):
                pass

    stream = Stream()
    if outpath:
        # need `str` stream in PY2 and PY3
        out = open(outpath, 'w')

    doc = LibraryDocumentation(library, name, version, docformat)
    LibdocWriter(format).write(
        doc, stream if format != 'html' else HTML(stream, **options))

    if out is not None:
        if outpath:
            out.close()
        return stream.count

    # else return the text from StringIO
    stream.seek(0)
    text = stream.read()
    StringIO.close(stream) # close was overridden
    return text


def xml(library, out=None, name=None, version=None, docformat=None):
    """Call :func:`robottools.libdoc` with ``format='xml'``.
    """
    return libdoc(library, out, name=name, version=version, format='xml',
                  docformat=docformat)

xml.__qualname__ = 'libdoc.xml'
libdoc.xml = xml


def html(library, out=None, name=None, version=None, docformat=None,
         **options):
    """Call :func:`robottools.libdoc` with ``format='html'``
       and extra `options` for HTML post-processing
       (see :func:`robottools.libdoc` for details).
    """
    return libdoc(library, out, name=name, version=version, format='html',
                  docformat=docformat, **options)

html.__qualname__ = 'libdoc.html'
libdoc.html = html
