# -*- coding: utf-8 -*-
"""Test the request wrapper."""

from malt import Request
import pytest


def test_environ():
    request = Request({
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'SCRIPT_NAME': '/app',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '5000',
        'wsgi.url_scheme': 'http',
    })
    assert request.method == 'GET'
    assert request.path == '/'
    assert request.script_name == '/app'
    assert request.host == 'localhost'
    assert request.port == '5000'
    assert request.scheme == 'http'
    return request.url == 'http://localhost:5000/app/'


def test_headers():
    request = Request({
        'HTTP_X_AUTH_KEY': 'the auth key',
    })
    assert request.headers['X-Auth-Key'] == 'the auth key'
    assert request.headers.get('X-Auth-Key') == 'the auth key'
    assert request.headers.get('X-Auth-Key', 'abc') == 'the auth key'

    with pytest.raises(KeyError) as exc_info:
        request.headers['X-Missing']
    assert exc_info.value.args[0] == 'X-Missing'

    assert request.headers.get('X-Missing') == None
    assert request.headers.get('X-Missing', 'abc') == 'abc'
