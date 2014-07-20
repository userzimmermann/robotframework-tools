# zetup.py
#
# My common stuff for Python package setups.
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import re
from collections import OrderedDict
from pkg_resources import (
  get_distribution, parse_version, parse_requirements,
  DistributionNotFound, VersionConflict)

if sys.version_info[0] == 3:
    from configparser import ConfigParser
    # Just for simpler PY2/3 compatible code:
    unicode = str
else:
    from ConfigParser import ConfigParser

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Try to get the directory of this script,
#  to correctly access VERSION, requirements.txt, ...
try:
    __file__
except: # Happens if exec()'d from SConstruct
    ZETUP_DIR = '.'
else:
    ZETUP_DIR = os.path.realpath(os.path.dirname(__file__))


class Distribution(str):
    def find(self, modpath, raise_=True):
        dist = get_distribution(self)
        if os.path.realpath(dist.location) \
          != os.path.realpath(os.path.dirname(modpath)):
            return None
        if dist.parsed_version != VERSION.parsed:
            if raise_:
                raise VersionConflict(
                  "Version of distribution %s"
                  " doesn't match %s.__version__ %s."
                  % (dist, PACKAGE, VERSION))
            return None
        return dist


class Version(str):
    """Manage and compare version strings
       using :func:`pkg_resources.parse_version`.
    """
    @staticmethod
    def _parsed(value):
        """Parse a version `value` if needed.
        """
        if isinstance(value, (str, unicode)):
            value = parse_version(value)
        return value

    @property
    def parsed(self):
        """The version string as parsed version tuple.
        """
        return parse_version(self)

    def __eq__(self, other):
        return self.parsed == self._parsed(other)

    def __ne__(self, other):
        return self.parsed != self._parsed(other)

    def __lt__(self, other):
        return self.parsed < self._parsed(other)

    def __le__(self, other):
        return self.parsed <= self._parsed(other)

    def __gt__(self, other):
        return self.parsed > self._parsed(other)

    def __ge__(self, other):
        return self.parsed >= self._parsed(other)


class Requirements(str):
    """Package requirements manager.
    """
    def __new__(cls, text):
        reqs = parse_requirements(text)
        return str.__new__(cls, '\n'.join(map(str, reqs)))

    def __init__(self, text):
        """Parse a requirements `text` and store a list
           of pkg_reqsources.Requirement instances.

        - Additionally looks for "# modname" comments after requirement lines
          (the actual root module name of the required package)
          and stores them as .modname attrs on the Requirement instances.
        """
        def reqs(): # Generate the parsed requirements from text:
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                try:
                    req, modname = line.split('#')
                except ValueError:
                    req = next(parse_requirements(line))
                    req.modname = req.key
                else:
                    req = next(parse_requirements(req))
                    req.modname = modname.strip()
                yield req
        self._list = list(reqs())

    def check(self, raise_=True):
        for req in self:
            try:
                mod = __import__(req.modname)
            except:
                if raise_:
                    raise DistributionNotFound(str(req))
                return False
            if mod.__version__ not in req:
                if raise_:
                    raise VersionConflict(
                      "Need %s. Found %s" % (str(req), mod.__version__))
                return False
        return True

    @property
    def checked(self):
        self.check()
        return self

    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, name):
        """Get a requirement by its package name.
        """
        for req in self._list:
            if name in [req.key, req.unsafe_name]:
                return req
        raise KeyError(name)

    def __add__(self, text):
        """Return a new manager instance
           with additional requirements from `text`.
        """
        return type(self)('%s\n%s' % (
          # For simplicity:
          #  Just create explicit modname hints for every requirement:
          '\n'.join('%s # %s' % (req, req.modname) for req in self),
          text))

    def __repr__(self):
        return str(self)


class Extras(OrderedDict):
    """Package extra features/requirements manager.
    """
    def __setitem__(self, name, text):
        reqs = Requirements(text)
        OrderedDict.__setitem__(self, name, reqs)

    def __repr__(self):
        return "\n\n".join((
          "[%s]\n" % key + '\n'.join(map(str, reqs))
          for key, reqs in self.items()))


config = ConfigParser()
for fname in ['zetup.ini', 'zetup.cfg', 'zetuprc']:
    if config.read(fname):
        ##TODO: No print after installation (under pkg/zetup/):
        ## print("zetup: Using config from %s" % fname)
        ZETUP_DATA = [fname]
        break
else:
    raise RuntimeError("No zetup config found.")


NAME = config.sections()[0]
DISTRIBUTION = Distribution(NAME)

config = dict(config.items(NAME))

TITLE = config.get('title', NAME)
DESCRIPTION = config['description'].replace('\n', ' ')

AUTHOR = re.match(r'^([^<]+)<([^>]+)>$', config['author'])
AUTHOR, EMAIL = map(str.strip, AUTHOR.groups())
URL = config['url']

LICENSE = config['license']

PYTHON = config['python'].split()

PACKAGE = config.get('package', NAME)

CLASSIFIERS = config['classifiers'].strip() \
  .replace('\n::', ' ::').split('\n')
CLASSIFIERS.append('Programming Language :: Python')
for pyversion in PYTHON:
    CLASSIFIERS.append('Programming Language :: Python :: ' + pyversion)

KEYWORDS = config['keywords'].split()
if any(pyversion.startswith('3') for pyversion in PYTHON):
    KEYWORDS.append('python3')


ZETUP_DATA += ['VERSION', 'requirements.txt']

VERSION = Version(open(os.path.join(ZETUP_DIR, 'VERSION')).read().strip())

REQUIRES = Requirements(open(os.path.join(ZETUP_DIR, 'requirements.txt')).read())

# Extra requirements to use with setup's extras_require=
EXTRAS = Extras()
_re = re.compile(r'^requirements\.(?P<name>[^\.]+)\.txt$')
for fname in sorted(os.listdir(ZETUP_DIR)):
    match = _re.match(fname)
    if match:
        ZETUP_DATA.append(fname)

        EXTRAS[match.group('name')] = open(os.path.join(ZETUP_DIR, fname)).read()

def zetup(**setup_options):
    """Run setup() with options from zetup.cfg
       and explicit override `setup_options`.
    """
    for option, value in [
      ('name', NAME),
      ('version', VERSION),
      ('description', DESCRIPTION),
      ('author', AUTHOR),
      ('author_email', EMAIL),
      ('url', URL),
      ('license', LICENSE),
      ('install_requires', REQUIRES),
      ('extras_require', EXTRAS),
      ('classifiers', CLASSIFIERS),
      ('keywords', KEYWORDS),
      ]:
        setup_options.setdefault(option, value)
    return setup(**setup_options)


# If installed with pip, add all build directories and src/ subdirs
#  of implicitly downloaded requirements
#  to sys.path and os.environ['PYTHONPATH']
#  to make them importable during installation:
sysbuildpath = os.path.join(sys.prefix, 'build')
try:
    fnames = os.listdir(sysbuildpath)
except OSError:
    pass
else:
    if 'pip-delete-this-directory.txt' in fnames:
        pkgpaths = []
        for fn in fnames:
            path = os.path.join(sysbuildpath, fn)
            if not os.path.isdir(path):
                continue
            path = os.path.abspath(path)
            pkgpaths.append(path)

            srcpath = os.path.join(path, 'src')
            if os.path.isdir(srcpath):
                pkgpaths.append(srcpath)

        for path in pkgpaths:
            sys.path.insert(0, path)

        PYTHONPATH = os.environ.get('PYTHONPATH')
        PATH = ':'.join(pkgpaths)
        if PYTHONPATH is None:
            os.environ['PYTHONPATH'] = PATH
        else:
            os.environ['PYTHONPATH'] = ':'.join([PATH, PYTHONPATH])


try:
    from jinja2 import FileSystemLoader
    from jinjatools.scons import JinjaBuilder
except ImportError:
    pass
else:
    class README_Builder(JinjaBuilder):
        def __init__(self):
            JinjaBuilder.__init__(self, FileSystemLoader('.'), context={
              'SETUP': self.SETUP(),
              'REQUIRES': self.REQUIRES(REQUIRES),
              'EXTRAS': self.EXTRAS(),
              'INSTALL': self.INSTALL(),
              })

        def SETUP(self):
            mdtext = (
              "Supported __Python__ versions: %s"
              "\n\n"
              "### Requirements"
              "\n\n%s\n\n"
              % (", ".join("__%s__" % pyversion for pyversion in PYTHON),
                 self.REQUIRES()))
            if EXTRAS:
                mdtext += "%s\n\n" % self.EXTRAS()
            mdtext += (
              "### Installation"
              "\n\n%s"
              % self.INSTALL())
            return mdtext

        def REQUIRES(self, reqs=REQUIRES):
            return '\n'.join(
              "* [`%s`](\n"
              "    https://pypi.python.org/pypi/%s)" % (
                req, req.unsafe_name)
              for req in reqs)

        def EXTRAS(self):
            return '\n\n'.join(
              "Extra requirements for __[%s]__:\n\n" % key
              + self.REQUIRES(reqs)
              for key, reqs in EXTRAS.items())

        def INSTALL(self):
            mdtext = (
              "    python setup.py install"
              "\n\n"
              "Or with [pip](http://www.pip-installer.org):"
              "\n\n"
              "    pip install ."
              "\n\n"
              "Or get the latest release from [PyPI](\n"
              "  https://pypi.python.org/pypi/%s):"
              "\n\n"
              "    pip install %s"
              % tuple(2 * [NAME]))
            if EXTRAS:
              mdtext += (
                "\n\n"
                "* With all extra features:"
                "\n\n"
                "        pip install %s[%s]"
                % (NAME, ','.join(EXTRAS)))
            return mdtext


    README_BUILDER = README_Builder()
