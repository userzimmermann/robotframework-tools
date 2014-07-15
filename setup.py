exec(open('__init__.py').read())


zetup(
  package_dir={
    'robottools.zetup': '.',
    },
  packages=[
    'robottools',
    'robottools.zetup',
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
    'robottools.zetup': ZETUP_DATA,
    },
  )
