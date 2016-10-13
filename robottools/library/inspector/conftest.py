from robottools import TestLibraryInspector

import pytest


@pytest.fixture
def inspector(request, stdlibname):
    return TestLibraryInspector(stdlibname)
