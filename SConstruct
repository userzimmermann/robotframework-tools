from six import PY2


PROJECT = 'robotframework-tools'

exec(open('zetup.py'))


REQUIRES += (
  'robotframework >= 2.8' if PY2
  else 'robotframework-python3 >= 2.8.4'
  )


env = Environment(BUILDERS={'README': README_Builder()})

env.README('README.md', 'README.md.jinja')
