# -*- coding: utf-8 -*-
"""Some utility functions."""

from json import dumps
from .http import MIME_JSON
from .wrappers import Response


def json_response(data, **kwargs):
    kwargs.setdefault('mimetype', MIME_JSON)
    text = dumps(data, separators=(',', ':'), ensure_ascii=False,
                 sort_keys=True)
    return Response(text, **kwargs)
