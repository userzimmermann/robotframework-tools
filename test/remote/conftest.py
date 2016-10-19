import sys
from textwrap import dedent
from subprocess import Popen

from robottools import TestRobot
from robottools.remote import RemoteRobot

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
    return Popen([
        sys.executable, '-c', dedent("""
        __import__('robottools.remote').remote.RemoteRobot(
            [%s], allow_import=[%s]
        )""") % (', '.join(map(repr, REMOTE_LIBRARIES)),
                 ', '.join(map(repr, ALLOWED_REMOTE_IMPORTS)))])


@pytest.fixture(scope='module')
def robot_Remote(request):
    """Creates a ``TestRobot`` instance loading ``Remote`` library,
    which automatically connects to the external ``RemoteRobot`` instance
    created in ``process`` fixture.
    """
    robot = TestRobot('Test')
    robot.Import('Remote')
    return robot
