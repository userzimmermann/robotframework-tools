import sys
from distutils.core import setup

setup(
  name = 'robotframework-tools',
  version = '0.1a2',
  description = (
    'Tools for Robot Framework and Test Libraries.'
    ),
  author = 'Stefan Zimmermann',
  author_email = 'zimmermann.code@gmail.com',

  license = 'GPLv3',

  packages = ['robottools', 'robottools.library'],

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
