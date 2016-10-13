from robottools import TestRobot

import pytest


@pytest.fixture
def robot(request, stdlibname):
    robot = TestRobot('Test')
    robot.Import(stdlibname)
    return robot


@pytest.fixture
def robot_no_BuiltIn(request, stdlibname):
    robot = TestRobot('Test', BuiltIn=False)
    robot.Import(stdlibname)
    return robot
