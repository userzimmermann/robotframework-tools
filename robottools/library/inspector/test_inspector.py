from inspect import getmembers, ismethod
from itertools import chain
from six.moves import zip

from moretools import camelize, isidentifier

from robot.utils import normalize
from robot.errors import DataError

import robottools.library.inspector
from robottools import TestLibraryInspector, TestLibraryImportError

import pytest


class TestInspector(object):
    """Tests for :class:`robottools.TestLibraryInspector`.
    """
    def test_class(self):
        assert TestLibraryInspector \
            is robottools.library.inspector.TestLibraryInspector
        assert type(TestLibraryInspector) \
            is robottools.library.inspector.TestLibraryInspectorMeta

    def test__init__(self, stdlibname, stdlib):
        inspector = TestLibraryInspector(stdlibname)
        assert type(inspector._library.get_instance()) is type(stdlib)

    def test_name(self, inspector, stdlibname):
        assert inspector.name == stdlibname

    def test__iter__(self, inspector, stdlib, stdlib_kwfuncnames):
        kwnames = [camelize(n, joiner=' ') for n in stdlib_kwfuncnames]
        for keyword in iter(inspector):
            assert isinstance(
                keyword, robottools.library.inspector.KeywordInspector)
            kwnames.remove(keyword.name)
        assert not kwnames

    def test__dir__(self, inspector, stdlib):
        # filter keyword methods from directly instantiated stdlib
        kwfuncnames = [name for name, obj in getmembers(stdlib)
                       if name[0] != '_' and ismethod(obj)]
        # and check if __dir__ contains their camelized names
        assert set(dir(inspector)) \
            == set(chain(map(camelize, kwfuncnames),
                         # as well as all other members
                         super(TestLibraryInspector, inspector).__dir__()))

    def test__getattr__(self, inspector, stdlib):
        # filter keyword methods from directly instantiated stdlib
        kwfuncnames = [name for name, obj in getmembers(stdlib)
                       if name[0] != '_' and ismethod(obj)]
        # and check that __getattr__ works with with keyword method names
        # as well as with normalized and camelized keyword names
        for name, normalized, camelized in zip(
                kwfuncnames, map(normalize, kwfuncnames),
                map(camelize, kwfuncnames)
        ):
            keyword, from_normalized, from_camelized = (
                getattr(inspector, n)
                for n in [name, normalized, camelized])
            assert keyword == from_normalized == from_camelized
            for keyword in [keyword, from_normalized, from_camelized]:
                assert isinstance(
                    keyword, robottools.library.inspector.KeywordInspector)
                assert keyword.name == camelize(name, joiner=' ')

    def test__getattr__error(self, inspector):
        with pytest.raises(AttributeError) as exc:
            getattr(inspector, 'Invalid')
        # and check that exception message contains
        # RFW's original exception message
        with pytest.raises(DataError) as robot_exc:
            if hasattr(inspector._library, 'get_handler'):
                # robot < 2.9
                inspector._library.get_handler('Invalid')
            else:
                inspector._library.handlers['Invalid']
        assert str(robot_exc.value) in str(exc.value)

    def test__repr__(self, inspector, stdlibname):
        assert repr(inspector) == "[Library] %s" % stdlibname
