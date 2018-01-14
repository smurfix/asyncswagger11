#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2018, Matthias Urlichs
#

"""Setup script
"""

import os

from setuptools import setup

setup(
    name="aioswagger11",
    version="0.1.0",
    license="BSD 3-Clause License",
    description="Asynchronous library for accessing Swagger-1.1-enabled APIs",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Matthias Urlichs",
    author_email="<matthias@urlichs.de>",
    url="https://github.com/smurfix/aioswagger11",
    packages=["aioswagger11"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
    ],
    tests_require=["nose", "tissue", "coverage", "httpretty"],
    install_requires=[],
    entry_points="""
    [console_scripts]
    swagger11-codegen = aioswagger11.codegen:main
    """
)
