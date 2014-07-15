exec(open('__init__.py').read())


zetup(
  package_dir={
    'robottools.setup': '.',
    },
  packages=[
    'robottools',
    'robottools.setup',
    'robottools.library',
    'robottools.library.keywords',
    'robottools.library.session',
    'robottools.library.context',
    'robottools.library.inspector',
    'robottools.testrobot',
    'robottools.remote',
    'robotshell',
    'robotshell.magic',
    ],
  py_modules=[
    'ToolsLibrary',
    ],
  package_data={
    'robottools.setup': ZETUP_DATA,
    },
  )
