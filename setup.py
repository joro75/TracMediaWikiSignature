#!/usr/bin/env python2
# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.


from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

PluginHomepageURL = 'https://github.com/joro75/TracMediaWikiSignature'

setup(
    name='TracMediaWikiSignature',
    install_requires=['Trac'],
    description='Trac plugin for using the MediaWiki signature in wiki pages',
    keywords='trac wiki plugin',
    platforms='any',
    version='1.0.0.0',
    license='MIT',
    author='John de Rooij',
    author_email='john.de.rooij@gmail.com',
    url=PluginHomepageURL,
    long_description=long_description,
    classifiers=[
      "Framework :: Trac",
      "Programming Language :: Python :: 2.7",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=['*.tests*']),
    package_data={
        '': ['LICENSE', 'README.md'],
        },
    entry_points = {
        'trac.plugins': [
            'TracMediaWikiSignature = tracplugins.mediawikisignature',
        ],
    },
)
