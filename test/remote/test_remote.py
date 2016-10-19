from six import text_type as unicode
from time import sleep

from decorator import decorate

from robottools import TestRobot

import pytest


def check_process(func):
    """Decorator for ``TestRemoteRobot.test_...`` methods
    to check if the external ``RemoteRobot`` process is still running,
    which is passed to every test method as ``process`` fixture.
    """
    def caller(func, self, process, *args, **kwargs):
        # polling returns None as long as process is running
        assert process.poll() is None, \
            "RemoteRobot process is not running (anymore)."
        return func(self, process, *args, **kwargs)

    return decorate(func, caller)


class TestRemoteRobot(object):
    """Integration tests for ``RemoteRobot`` and ``TestRobot``.
    """
    @check_process
    def test_bool_result(self, process, robot_Remote):
        for value in [True, 1, 2.3, b'four', u'five', [5], {'six': 7}]:
            assert robot_Remote.ConvertToBool(value) is True
        for value in [False, 0, 0.0, b'', u'', [], {}]:
            assert robot_Remote.ConvertToBool('') is False

    @check_process
    def test_int_result(self, process, robot_Remote):
        for value in [1, 2.3, '4', u'5']:
            result = robot_Remote.ConvertToInteger(value)
            assert isinstance(result, int)
            assert result == int(value)

    @check_process
    def test_float_result(self, process, robot_Remote):
        for value in [1, 2.3, '4.5', u'6.7']:
            result = robot_Remote.ConvertToNumber(value)
            assert isinstance(result, float)
            assert result == float(value)

    @check_process
    def test_bytes_result(self, process, robot_Remote):
        for value in [b'bytes', u'bytes']:
            result = robot_Remote.ConvertToBytes(value)
            assert isinstance(result, bytes)
            assert result == b'bytes'

    @check_process
    def test_string_result(self, process, robot_Remote):
        for value in [1, 2.3, 'four', u'five']:
            result = robot_Remote.ConvertToString(value)
            assert isinstance(result, unicode)
            assert result == unicode(value)

    @check_process
    def test_ImportRemoteLibrary(self, process, robot_Remote):
        assert not hasattr(robot_Remote, 'CopyList')
        robot_Remote.ImportRemoteLibrary('Collections')
        robot = TestRobot('New')
        robot.Import('Remote')
        assert robot.CopyList

    @check_process
    def test_StopRemoteServer(self, process, robot_Remote):
        assert robot_Remote.StopRemoteServer() is True
        process.wait()
        # polling returns None as long as process is running
        assert process.poll() is not None
