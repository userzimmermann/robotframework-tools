exec(open('__init__.py'))


env = Environment(BUILDERS={'README': README_Builder()})

env.README('README.md', 'README.md.jinja')
