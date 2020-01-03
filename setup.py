# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.


from setuptools import find_packages, setup

PluginHomepageURL = 'https://github.com/joro75/TracMediaWikiSignature'

setup(
    name='TracMediaWikiSignature',
    install_requires='Trac >=1.0dev',
    description='Trac plugin for using the MediaWiki signature in wiki pages',
    keywords='trac wiki plugin',
    platforms='any',
    version='0.8.0.1',
    license='MIT',
    author='John de Rooij',
    author_email='john.de.rooij@gmail.com',
    url=PluginHomepageURL,
    long_description="""
      This plugin for Trac 1.0 provides support for using the 
      MediaWiki signature ('~~~~') during wiki page editing, where
      the signature will be replaced by the editors username and the
      date and time of the edit.
      """,
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