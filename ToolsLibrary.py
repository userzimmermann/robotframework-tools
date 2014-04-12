import robot.running
from robot.running.namespace import IMPORTER

from BuiltIn import BuiltIn

from robottools import testlibrary


BUILTIN = BuiltIn()


TestLibrary = testlibrary()
keyword = TestLibrary.keyword


class ToolsLibrary(TestLibrary):

    @keyword
    def reload_library(self, name, *args):
        """Reload an already imported Test Library
           with given name and optional args.

        This also leads to a reload of the Test Library Keywords,
        which allows Test Libraries to dynamically extend or change them.
        """
        #HACK
        libs = BUILTIN._namespace._testlibs
        if name not in libs:
            raise RuntimeError(
              "Test Library '%s' was not imported yet." % name)
        del libs[name]
        #HACK even worse :)
        cache = IMPORTER._library_cache
        lib = robot.running.TestLibrary(name, args)
        key = (name, lib.positional_args, lib.named_args)
        key = cache._norm_path_key(key)
        try:
            index = cache._keys.index(key)
        except ValueError:
            pass
        else:
            cache._keys.pop(index)
            cache._items.pop(index)

        BUILTIN.import_library(name, *args)
