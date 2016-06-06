# -*- coding: utf-8 -*-
"""Some utility functions."""

from json import dumps
from .http import MIME_JSON
from .wrappers import Response


def json_response(data, pretty=False, **kwargs):
    kwargs.setdefault('mimetype', MIME_JSON)
    if pretty:
        kwargs.setdefault('ensure_ascii', True)
        kwargs.setdefault('separators', None)
        kwargs.setdefault('indent', 2)
    else:
        kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('separators', (',', ':'))
        kwargs.setdefault('indent', None)

    text = dumps(data,
                 ensure_ascii=kwargs.pop('ensure_ascii'),
                 separators=kwargs.pop('separators'),
                 indent=kwargs.pop('indent'),
                 sort_keys=True) + u'\n'
    return Response(text, **kwargs)
