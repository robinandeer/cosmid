import genie

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'An automated genomics database updater.',
    'author': 'Robin Andeer',
    'url': 'https://github.com/robinandeer/Genie.',
    'download_url': 'https://github.com/robinandeer/Genie/archive/master.zip',
    'author_email': 'robin.andeer@scilifelab.se',
    'version': genie.__version__,
    'install_requires': [
        "nose",
        "ftputil",
        "sh",
        "watchdog",
        "roadblock",
        "docopt"
    ],
    'packages': ['genie'],
    'scripts': ["scripts/genie.py"],
    'name': 'Genie'
}

setup(**config)
