
# -*- coding: utf-8 -*-

# A Python implementation of geodesy tools for various ellipsoidal and
# spherical earth models using trigonometric and vector-based methods.

# All modules have been checked* statically with PyChecker, PyFlakes,
# PyCodeStyle (formerly Pep8), McCabe using Python 2.7.10 and 2.7.13
# and with Flake8 on Python 3.6.0.  The tests have been run with 64-bit
# Python 2.6.9, 2.7.10, 2.7.13, 3.5.2 and 3.6.0, but only on MacOS
# 10.10 Yosemite, MacOS 10.11 El Capitan and/or MacOS 10.12.2 Sierra.

# Transcribed from JavaScript originals by (C) Chris Veness 2005-2016
# and published under the same MIT Licence**.

# For more information and further details see:

# <https://github.com/chrisveness/geodesy/>
# <http://www.movable-type.co.uk/scripts/latlong.html>
# <http://www.movable-type.co.uk/scripts/latlong-vincenty.html>
# <http://www.movable-type.co.uk/scripts/latlong-vectors.html>
# <http://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html>
# <http://www.movable-type.co.uk/scripts/latlong-os-gridref.html>

# __
# *) <http://code.activestate.com/recipes/546532-pychecker-postprocessor/>

try:
    import datum as _  # PYCHOK expected
    del _
except ImportError:
    # extend sys.path for Python 3+
    import os, sys  # PYCHOK expected
    sys.path.insert(0, os.path.dirname(__file__))
    del os, sys

from datum import *  # PYCHOK __all__
from dms   import *  # PYCHOK __all__
from lcc   import *  # PYCHOK __all__
from mgrs  import *  # PYCHOK __all__
from osgr  import *  # PYCHOK __all__
from utils import *  # PYCHOK __all__
from utm   import *  # PYCHOK __all__
import ellipsoidalNvector  # PYCHOK false
import ellipsoidalVincenty  # PYCHOK false
import sphericalNvector  # PYCHOK false
import sphericalTrigonometry  # PYCHOK false

VincentyError = ellipsoidalVincenty.VincentyError

# all public contants, classes and functions
__all__ = ('ellipsoidalNvector', 'ellipsoidalVincenty',
           'sphericalNvector', 'sphericalTrigonometry',
           'VincentyError')  # extended below
__version__ = '17.02.01'

# lift all public constants, functions, etc.
import datum as _datum, dms as _dms, mgrs as _mgrs, \
       utils as _utils, utm as _utm, osgr as _osgr, \
       lcc as _lcc  # PYCHOK expected
for m in (_datum, _dms, _mgrs, _osgr, _utm, _utils, _lcc):
    __all__ += m.__all__
del m, _datum, _dms, _mgrs, _osgr, _utm, _utils, _lcc

# **) MIT License
#
# Copyright (C) 2016-2017 -- mrJean1@Gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
