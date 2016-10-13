from importlib import import_module
from inspect import getmembers, ismethod

import robot

import pytest


@pytest.fixture(params=['String', 'Collections'])
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
def stdlib_kwfuncnames(request, stdlib):
    return [name for name, obj in getmembers(stdlib)
            if name[0] != '_' and ismethod(obj)]


@pytest.fixture
def BuiltIn_kwfuncnames(request):
    BuiltIn = stdlib(request, 'BuiltIn')
    return stdlib_kwfuncnames(request, BuiltIn)
