#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Setup script
"""

import os

from setuptools import setup

setup(
    name="aioswagger11",
    version="0.2.2",
    license="BSD 3-Clause License",
    description="Library for accessing Swagger-1.1-enabled APIs",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc.",
    author_email="dlee@digium.com",
    url="https://github.com/smurfix/aioswagger11",
    packages=["aioswagger11"],
    classifiers=[
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python3",
    ],
    tests_require=["nose", "tissue", "coverage", "httpretty"],
    install_requires=[],
    entry_points="""
    [console_scripts]
    swagger11-codegen = aioswagger11.codegen:main
    """
)
