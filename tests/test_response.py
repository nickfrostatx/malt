# -*- coding: utf-8 -*-
"""Test the request wrapper."""

from malt import Response
import pytest


def test_status_code():
    assert Response('').status_code == 200
    assert Response('', 418).status_code == 418


def test_status_text():
    assert Response('').status == '200 OK'
    assert Response('', 100).status == '100 Continue'
    assert Response('', 418).status == '418 I\'m a teapot'


def test_status_invalid():
    with pytest.raises(ValueError) as exc:
        Response('', 200.)
    assert 'Invalid status: 200.0' in str(exc)

    for code in (100., '', '200', -15, 0, 199, 600):
        with pytest.raises(ValueError) as exc:
            Response('').status_code = code
        assert 'Invalid status: ' + repr(code) in str(exc)
