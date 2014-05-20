#!/usr/bin/env python
import sys
import os

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    try:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup
        from setuptools.command.test import test as TestCommand
    except Exception as e:
        print("Forget setuptools, trying distutils...")
        from distutils.core import setup

root = os.path.dirname(os.path.realpath(__file__))
description = "Python Cognitive Modelling Suite "
setup(
    name="ccmsuite",
    version=0.1,
    author="Terry Stewart",
    author_email="tcstewar@uwaterloo.ca",
    packages=['ccm'],
    scripts=[],
    url="https://github.com/tcstewar/ccmsuite",
    description=description,
)
