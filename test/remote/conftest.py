import sys
from six import PY2
from textwrap import dedent
from subprocess import Popen

from robot.errors import DataError

from robottools import TestRobot

import pytest


# the libraries to load in the RemoteRobot instance
# created in an external python process via process fixture
REMOTE_LIBRARIES = [
    'BuiltIn',
    'ToolsLibrary',
]
ALLOWED_REMOTE_IMPORTS = [
    'Collections',
]


@pytest.fixture(scope='module')
def process(request):
    """Creates an external python process with a ``RemoteRobot`` instance
    loading all libraries defined in ``REMOTE_LIBRARIES``.
    """
    # robotremoteserver is not PY3-compatible yet
    return PY2 and Popen([
        sys.executable, '-c',
        "__import__('robottools.remote').remote.RemoteRobot("
        "    [%s], allow_import=[%s])"
        % (', '.join(map(repr, REMOTE_LIBRARIES)),
           ', '.join(map(repr, ALLOWED_REMOTE_IMPORTS)))])


@pytest.fixture(scope='module')
def robot_Remote(request):
    """Creates a ``TestRobot`` instance loading ``Remote`` library,
    which automatically connects to the external ``RemoteRobot`` instance
    created in ``process`` fixture.
    """
    # make 3 connection attempts before bailing out
    for _ in range(3):
        try:
            # BuiltIn will also be served by RemoteRobot
            robot = TestRobot('Test', BuiltIn=False)
            robot.Import('Remote')
            return robot

        except DataError:
            continue
    raise
