import sys


exec(open('__init__.py').read())

REQUIRES += (
  'robotframework >= 2.8' if sys.version_info[0] == 2
  else 'robotframework-python3 >= 2.8.4'
  ) + ' # robot'


zetup(py_modules=['ToolsLibrary'])
