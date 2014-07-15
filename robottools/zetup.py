from path import path as Path

import robottools


__path__ = [Path(robottools.__path__[0]).abspath().dirname()]

__file__ = __path__[0] / '__init__.py'

with __path__[0]:
    exec(open(__file__).read())
