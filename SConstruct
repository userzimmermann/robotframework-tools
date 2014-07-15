exec(open('__init__.py').read())

REQUIRES += 'robotframework >= 2.8 # robot'


env = Environment(BUILDERS={'README': README_Builder()})

env.README('README.md', 'README.md.jinja')
