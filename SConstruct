exec(open('__init__.py').read())


env = Environment(BUILDERS={'README': README_Builder()})

env.README('README.md', 'README.md.jinja')
