import sys
from setuptools import setup
from pkg_resources import require, DistributionNotFound

if sys.version_info[0] == 3:
    try:
        require('robotframework-python3')
    except DistributionNotFound:
        sys.stderr.write(
          "\n"
          "Requires robotframework-python3."
          " This is unofficial."
          " You can get it from:"
          "\n\n"
          "https://bitbucket.org/userzimmermann/robotframework-python3"
          "\n\n")
        sys.exit(1)

setup(
  name='robotframework-tools',
  version='0.1a96',
  description=(
    'Python Tools for Robot Framework and Test Libraries.'
    ),
  author='Stefan Zimmermann',
  author_email='zimmermann.code@gmail.com',
  url='http://bitbucket.org/userzimmermann/robotframework-tools',

  license='GPLv3',

  install_requires=[
    'path.py',
    'moretools >= 0.1a26',
    'robotframework >= 2.8' if sys.version_info[0] < 3
    else 'robotframework-python3',
    ],
  packages=[
    'robottools',
    'robottools.library',
    'robottools.library.session',
    'robottools.library.inspector',
    'robottools.testrobot',
    'robotshell',
    'robotshell.magic',
    ],

  use_2to3=True,
  use_2to3_exclude_fixers=['lib2to3.fixes.fix_' + fix for fix in [
    'dict',
    'map',
    'filter',
    'reduce',
    ]],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords=[
    'robottools', 'robot', 'framework', 'robotframework', 'tools',
    'test', 'automation', 'testautomation',
    'testlibrary', 'testcase', 'keyword', 'pybot',
    'robotshell', 'ipython',
    'python3',
    ],
  )
