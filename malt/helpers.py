# -*- coding: utf-8 -*-
"""Some utility functions."""

text_type = type(u'')


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
