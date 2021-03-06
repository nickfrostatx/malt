# -*- coding: utf-8 -*-
"""Some utility functions."""
try:
    from urllib.parse import unquote as unquote_native
except ImportError:
    from urllib import unquote as unquote_native


text_type = type(u'')
PY2 = (str == bytes)
WSGI_WANT_BYTES = PY2

if PY2:
    from itertools import izip
else:
    izip = zip


def is_string(value):
    return isinstance(value, (bytes, text_type))


def want_bytes(value, charset='utf-8', errors='strict'):
    if isinstance(value, text_type):
        return value.encode(charset, errors)
    return value


def want_text(value, charset='utf-8', errors='strict'):
    if not isinstance(value, text_type):
        return value.decode(charset, errors)
    return value


def unquote(string, encoding='utf-8', errors='replace'):
    if PY2:
        return unquote_native(string.encode('latin1')).decode(encoding, errors)
    return unquote_native(string, encoding, errors)
