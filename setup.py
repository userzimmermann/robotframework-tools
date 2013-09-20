import sys
from setuptools import setup

setup(
  name = 'robotframework-tools',
  version = '0.1a69',
  description = (
    'Tools for Robot Framework and Test Libraries.'
    ),
  author = 'Stefan Zimmermann',
  author_email = 'zimmermann.code@gmail.com',
  url = 'http://bitbucket.org/userzimmermann/robotframework-tools',

  license = 'GPLv3',

  install_requires = [
    'moretools >= 0.1a25',
    'robotframework >= 2.8',
    ],
  packages = [
    'robottools',
    'robottools.library',
    'robottools.library.session',
    'robotshell',
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
    'robotshell', 'ipython',
    ],
  )
