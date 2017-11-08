#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Evedom Packaging Info
"""

__author__ = '(nam4dev) Namgyal Brisson'
__created__ = '08/11/2017'

from distutils.core import setup

setup(
    name='evedom',
    version='0.0.1',
    packages=['evedom', 'evedom.helpers'],
    url='',
    license='MIT',
    author='nam4dev',
    author_email='namat4css@gmail.com',
    description=(
        'Allow to manage python-eve endpoint(s) in a structured manner' 
        'and to get all endpoint(s) automatically loaded'
    ),
    keywords='eve evedom',
)
