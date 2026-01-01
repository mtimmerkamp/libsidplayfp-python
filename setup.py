#!/usr/bin/env python3
from setuptools import setup


setup(
    cffi_modules=["libsidplayfp/libsidplayfp_build.py:ffibuilder"],
)
