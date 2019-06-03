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
    name="asyncswagger11",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag"
    },
    license="BSD 3-Clause License",
    description="Asynchronous library for accessing Swagger-1.1-enabled APIs",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Matthias Urlichs",
    author_email="matthias@urlichs.de",
    url="https://github.com/M-o-a-T/asyncswagger11",
    packages=["asyncswagger11"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    tests_require=["pytest", "pytest-cov"],
    install_requires=["asks"],
    setup_requires=["setuptools_scm"],
    entry_points="""
    [console_scripts]
    swagger11-codegen = asyncswagger11.codegen:main
    """
)
