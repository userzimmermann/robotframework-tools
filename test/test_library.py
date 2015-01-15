import pytest

from robottools import testlibrary, istestlibraryclass


def test_testlibrary():
    """Test creation of Dynamic Test Library classes.
    """
    TestLibrary = testlibrary()

    assert istestlibraryclass(TestLibrary)

    assert not TestLibrary.session_handlers
    assert not TestLibrary.context_handlers
    assert not TestLibrary.keywords

    @TestLibrary.keyword
    def test_keyword(self):
        pass

    class LibraryNotCallingBaseInit(TestLibrary):
        def __init__(self):
            pass

    assert istestlibraryclass(LibraryNotCallingBaseInit)

    lib = LibraryNotCallingBaseInit()

    # check if methods complain about missing instance-bound keywords mapping
    for method, args in [
      (lib.get_keyword_names, []),
      (lib.get_keyword_arguments, ['test_keyword']),
      (lib.get_keyword_documentation, ['test_keyword']),
      (lib.run_keyword, ['test_keyword', []]),
      ]:
        with pytest.raises(RuntimeError) as e:
            method(*args)
        assert str(e.value).strip().endswith('base __init__ called?')
