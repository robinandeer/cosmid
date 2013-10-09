import cosmid

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    "name": "cosmid",
    "description": "A database manager for genomics",
    "author": "Robin Andeer",
    "url": "https://github.com/robinandeer/cosmid",
    "download_url": "https://github.com/robinandeer/cosmid/archive/master.zip",
    "author_email": "robin.andeer@scilifelab.se",
    "version": cosmid.__version__,
    "install_requires": [
        "nose",
        "ftputil",
        "docopt",
        "path.py",
        "pyyaml",
        "fuzzywuzzy",
        "termcolor"
    ],
    "packages": [
        "cosmid",
        "cosmid.resources",
        "cosmid.servers"
    ],
    "scripts": ["scripts/cosmid"]
}

setup(**config)
