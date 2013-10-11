# Bootstrap distribute unless already installed
from distribute_setup import use_setuptools
use_setuptools()

import os
import sys

from setuptools import setup, find_packages

import cosmid

# Shortcut for publishing to Pypi
# Source: https://github.com/kennethreitz/tablib/blob/develop/setup.py
if sys.argv[-1] == "publish":
  os.system("python setup.py sdist upload")
  sys.exit()

setup(
  name = "cosmid",
  version = cosmid.__version__,
  packages = find_packages(exclude=["tests"]),
  scripts = ["scripts/cosmid"],

  # Project dependencies
  install_requires = [
    "ftputil",
    "docopt",
    "path.py",
    "pyyaml",
    "fuzzywuzzy",
    "termcolor"
  ],

  # Packages required for testing
  tests_require = [
    "nose"
  ],

  # Metadate for upload to Pypi
  author = "Robin Andeer",
  author_email = "robin.andeer@scilifelab.se",
  description = "A genomics resource manager",
  long_description = (open('README.rst').read()),
  license = "MIT",
  keywords = "bioinformatics resource manager database genomics",
  url = "https://github.com/robinandeer/cosmid",
  download_url = "https://github.com/robinandeer/cosmid/releases",
  classifiers = (
    "Development Status :: 3 - Alpha",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python"
  )
)
