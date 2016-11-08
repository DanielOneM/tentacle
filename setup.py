"""Setup the EventEngine package."""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ONEm Event Engine',
    'author': 'Daniel Enache',
    'url': 'https://github.com/ONEmCommunications/tentacle.git',
    'download_url': 'https://github.com/ONEmCommunications/tentacle.git',
    'author_email': 'daniel.enache@onem.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': find_packages(),
    'scripts': [],
    'name': 'tentacle'
}

setup(**config)
