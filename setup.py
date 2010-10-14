# Copyright (c) 2010 Matt Harrison
from distutils.core import setup
#from setuptools import setup

from pgtweaklib import meta

setup(name='PgTweak',
      version=meta.__version__,
      author=meta.__author__,
      description='FILL IN',
      scripts=['bin/pgtweak'],
      package_dir={'pgtweaklib':'pgtweaklib'},
      packages=['pgtweaklib'],
)
