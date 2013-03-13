try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'An automatic genomics database updater.',
    'author': 'Robin Andeer',
    'url': 'https://github.com/robinandeer/Genie.',
    'download_url': 'https://github.com/robinandeer/Genie/archive/master.zip',
    'author_email': 'robin.andeer@scilifelab.se',
    'version': '0.3.2',
    'install_requires': ['nose'],
    'packages': ['genie'],
    'scripts': ['bin/update_databases.py'],
    'name': 'Genie'
}

setup(**config)
