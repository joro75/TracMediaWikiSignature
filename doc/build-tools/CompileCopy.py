#!/usr/bin/env python2
# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

import sys
import subprocess
import glob
import shutil

got_modules = True

# Check if wheel is present
try:
    import wheel
except ImportError:
    # Wheel is not present, try to install it
    print("The Wheel pip package in missing. Execute: 'pip install wheel'")
    got_modules = False

if got_modules:
    if 'win32' in sys.platform:
        subprocess.call(r'py setup.py bdist_egg sdist bdist_wheel')
        files = glob.glob('dist\TracMediaWikiSignature-*-py*.*.egg')
        if len(files):
            shutil.copy2(files[0], r'L:\Products\Trac\plugins')

# The Trac installation will automatically detect that a newer version is available
# and will use the updated plugin.