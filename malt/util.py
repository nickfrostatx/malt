# -*- coding: utf-8 -*-
"""Some utility functions."""

from json import dumps
from .wrappers import Response


def json_response(data, **kwargs):
    kwargs.setdefault('mimetype', 'application/json')
    return Response(dumps(data, separators=(',',':')), **kwargs)
