import zetup
from moretools import camelize

from robot.utils import normalize

import robottools.testrobot

import pytest


class TestRobot(object):

    def test__dir__(self, robot, BuiltIn_kwfuncnames,
                    stdlib, stdlib_kwfuncnames
    ):
        # check that all camelized Keyword names from BuiltIn
        assert not set(map(camelize, BuiltIn_kwfuncnames)) - set(dir(robot))
        # ... and the additionally loaded standrad Library are included
        assert not set(map(camelize, stdlib_kwfuncnames)) - set(dir(robot))

        assert not set(zetup.object.__dir__(robot)) - set(dir(robot))

    def test__dir__no_BuiltIn(self, robot_no_BuiltIn, BuiltIn_kwfuncnames,
                              stdlib, stdlib_kwfuncnames
    ):
        # check that no BuiltIn Keywords are reported
        assert set(map(camelize, BuiltIn_kwfuncnames)) \
            - set(dir(robot_no_BuiltIn)) \
            == set(map(camelize, BuiltIn_kwfuncnames))
        # but the imported standard lib's are
        assert not (set(map(camelize, stdlib_kwfuncnames))
                    - set(dir(robot_no_BuiltIn)))
        assert not (set(map(camelize, stdlib_kwfuncnames))
                    - set(dir(robot_no_BuiltIn)))

    def test__getattr__BuiltIn(self, robot, BuiltIn_kwfuncnames,
                               stdlibname, stdlib_kwfuncnames
    ):
        # check that BuiltIn Library access works
        BuiltIn = robot.BuiltIn
        lib = getattr(robot, stdlibname)
        assert isinstance(BuiltIn, robottools.testrobot.TestLibrary)
        assert BuiltIn.name == 'BuiltIn'
        assert not set(map(camelize, BuiltIn_kwfuncnames)) - set(dir(BuiltIn))
        assert isinstance(lib, robottools.testrobot.TestLibrary)
        assert lib.name == stdlibname
        assert not set(map(camelize, stdlib_kwfuncnames)) - set(dir(lib))

    def test__getattr__Library(self, robot, stdlibname, stdlib_kwfuncnames):
        # check that access to additionally imported standard Library works
        lib = getattr(robot, stdlibname)
        assert isinstance(lib, robottools.testrobot.TestLibrary)
        assert lib.name == stdlibname
        assert not set(map(camelize, stdlib_kwfuncnames)) - set(dir(lib))

    def test__getattr__no_BuiltIn(self, robot_no_BuiltIn,
                                  stdlibname, stdlib_kwfuncnames
    ):
        # check that BuiltIn Library is not availabe
        with pytest.raises(Exception):
            robot_no_BuiltIn.BuiltIn
        # ... but that access to additionally imported standard Library works
        self.test__getattr__Library(
            robot_no_BuiltIn, stdlibname, stdlib_kwfuncnames)

    def check__getattr__Keyword(self, robot, libname, kwfuncnames):
        """Helper method to check that access to all Keywords
        given by their original function names works
        in different name formats.
        """
        for funcname, camelized, normalized in zip(
                kwfuncnames, map(camelize, kwfuncnames),
                map(normalize, kwfuncnames)
        ):
            for name in funcname, camelized, normalized:
                keyword = getattr(robot, name)
                assert isinstance(keyword, robottools.testrobot.Keyword)
                assert keyword.name == camelize(funcname, joiner=' ')
                assert keyword.libname == libname

    def test__getattr__BuiltIn_Keyword(self, robot, BuiltIn_kwfuncnames):
        # check that access to BuiltIn Keywords works
        self.check__getattr__Keyword(robot, 'BuiltIn', BuiltIn_kwfuncnames)

    def test__getattr__Keyword(self, robot, stdlibname, stdlib_kwfuncnames):
        # check that access to all Keywords
        # from imported standard Library works
        self.check__getattr__Keyword(robot, stdlibname, stdlib_kwfuncnames)

    def test__getattr__NoBuiltIn(self, robot_no_BuiltIn, BuiltIn_kwfuncnames,
                                 stdlibname, stdlib_kwfuncnames
    ):
        # check that NO BuiltIn Keywords are available
        for funcname, camelized, normalized in zip(
                BuiltIn_kwfuncnames, map(camelize, BuiltIn_kwfuncnames),
                map(normalize, BuiltIn_kwfuncnames)
        ):
            for name in funcname, camelized, normalized:
                with pytest.raises(AttributeError):
                    keyword = getattr(robot_no_BuiltIn, name)
        # ... but that access to all Keywords
        # from imported standard Library works
        self.check__getattr__Keyword(
            robot_no_BuiltIn, stdlibname, stdlib_kwfuncnames)
