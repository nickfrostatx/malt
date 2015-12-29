# -*- coding: utf-8 -*-
"""
Minimalistic WSGI framework.

:copyright: (c) 2015 by Nicholas Frost.
:license: MIT, see LICENSE for more details.
"""

from .app import Malt
from .exceptions import HTTPException
from .wrappers import Request, Response

__author__ = 'Nick Frost'
__copyright__ = 'Copyright 2015, Nicholas Frost'
__license__ = 'MIT'
__version__ = '0.1.dev0'
__email__ = 'nickfrostatx@gmail.com'
