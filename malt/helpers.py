# -*- coding: utf-8 -*-
"""Some utility functions."""

unicode_type = type(u'')


def is_text(value):
    return isinstance(value, (bytes, unicode_type))
