#!/usr/bin/env python3

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='libsidplayfp',

    version='0.0.4a0',

    description='interface to libsidplayfp',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/mtimmerkamp/libsidplayfp-python',

    # Author details
    author='Maximilian Timmerkamp',
    author_email='maximilian.timmerkamp@posteo.de',

    license='GNU General Public License v3 or later (GPLv3+)',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Software Development :: Libraries',

        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='sidplayfp libsidplayfp c64 sidtune',

    packages=find_packages(exclude=['doc']),

    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["libsidplayfp/libsidplayfp_build.py:ffibuilder"],

    install_requires=['cffi>=1.0.0'],
)
