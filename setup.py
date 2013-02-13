import sys
from distutils.core import setup

setup(
  name = 'robotframework-tools',
  version = '0.1a6',
  description = (
    'Tools for Robot Framework and Test Libraries.'
    ),
  author = 'Stefan Zimmermann',
  author_email = 'zimmermann.code@gmail.com',

  license = 'GPLv3',

  install_requires = [
    'python-moretools >= 0.1a6',
    ],
  packages = [
    'robottools',
    'robottools.library',
    'robottools.library.session',
    ],

  classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ],
  keywords = [
    'robottools', 'robot', 'framework', 'robotframework', 'tools',
    'test', 'automation', 'testautomation',
    'testlibrary', 'testcase', 'keyword', 'pybot',
    ],
  )
