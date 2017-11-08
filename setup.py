#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Evedom Packaging Settings
"""

__author__ = '(nam4dev) Namgyal Brisson'
__created__ = '08/11/2017'

from distutils.core import setup

setup(
    name='evedom',
    version='0.0.1',
    packages=['evedom', 'evedom.helpers'],
    url='https://github.com/nam4dev/evedom',
    license='MIT',
    author='nam4dev',
    author_email='namat4css@gmail.com',
    description=(
        'Allow to manage python-eve endpoint(s) in a structured manner'
        'and to get all endpoint(s) automatically loaded'
    ),
    keywords='eve evedom',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
