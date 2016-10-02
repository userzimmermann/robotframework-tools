from importlib import import_module

import robot

from robottools import TestLibraryInspector

import pytest


@pytest.fixture(params=['BuiltIn', 'String', 'Collections'])
def stdlibname(request):
    return request.param


@pytest.fixture
def stdlib(request, stdlibname):
    try: # Robot < 3.0
        libmod = import_module(stdlibname)
    except ImportError:
        libmod = import_module('robot.libraries.%s' % stdlibname)
    libcls = getattr(libmod, stdlibname)
    return libcls()


@pytest.fixture
def inspector(request, stdlibname):
    return TestLibraryInspector(stdlibname)
