from importlib import import_module

from robottools import TestLibraryInspector

import pytest


@pytest.fixture(params=['BuiltIn', 'String', 'Collections'])
def stdlibname(request):
    return request.param


@pytest.fixture
def stdlib(request, stdlibname):
    libmod = import_module('robot.libraries.%s' % stdlibname)
    libcls = getattr(libmod, stdlibname)
    return libcls()


@pytest.fixture
def inspector(request, stdlibname):
    return TestLibraryInspector(stdlibname)
