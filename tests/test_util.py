# -*- coding: utf-8 -*-
"""Test out the utility functions."""

from malt import json


def test_json():
    resp = json({'greeting': 'Hello World!'})

    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
    assert list(resp) == [b'{"greeting":"Hello World!"}']
