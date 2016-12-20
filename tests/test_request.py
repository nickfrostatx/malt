# -*- coding: utf-8 -*-
"""Test the request wrapper."""

from malt import HTTPException, Request
import io
import pytest


def test_environ():
    request = Request({
        'PATH_INFO': '/',
        'REQUEST_METHOD': 'GET',
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


def test_url():
    def req(env):
        base_environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SCRIPT_NAME': '/app',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.url_scheme': 'http',
        }
        base_environ.update(env)
        return Request(base_environ)

    assert req({}).url == 'http://localhost:5000/app/'
    assert req({'SERVER_PORT': '80'}).url == 'http://localhost/app/'
    assert req({'SERVER_PORT': '443'}).url == 'http://localhost:443/app/'

    assert req({
                    'wsgi.url_scheme': 'https',
                }).url == 'https://localhost:5000/app/'

    assert req({
                    'wsgi.url_scheme': 'https',
                    'SERVER_PORT': '80',
                }).url == 'https://localhost:80/app/'
    assert req({
                    'wsgi.url_scheme': 'https',
                    'SERVER_PORT': '443',
                }).url == 'https://localhost/app/'

    assert req({'PATH_INFO': '/path'}).url == 'http://localhost:5000/app/path'
    assert req({'SCRIPT_NAME': ''}).url == 'http://localhost:5000/'

    assert req({'QUERY_STRING': ''}).url == 'http://localhost:5000/app/'
    assert req({'QUERY_STRING': 'a'}).url == 'http://localhost:5000/app/?a'

    assert req({'HTTP_HOST': 'google.com'}).url == 'http://google.com/app/'


def test_headers():
    request = Request({
        'CONTENT_TYPE': 'text/plain; charset=utf-8',
        'CONTENT_LENGTH': '42',
        'HTTP_HOST': 'example.com',
        'HTTP_X_AUTH_KEY': 'the auth key',
        'SERVER_NAME': 'localhost',
    })
    assert request.headers['X-Auth-Key'] == 'the auth key'
    assert request.headers.get('X-Auth-Key') == 'the auth key'
    assert request.headers.get('X-Auth-Key', 'abc') == 'the auth key'
    assert request.host == 'example.com'

    with pytest.raises(KeyError) as exc_info:
        request.headers['X-Missing']
    assert exc_info.value.args[0] == 'X-Missing'

    assert request.headers.get('X-Missing') is None
    assert request.headers.get('X-Missing', 'abc') == 'abc'

    assert request.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert request.headers['Content-Length'] == '42'

    assert 'X-Missing' not in request.headers
    assert 'Content-Type' in request.headers
    assert 'CoNtEnT-LeNgTh' in request.headers
    assert 'x-AuTh-KeY' in request.headers

    assert set(request.headers) == set(['Content-Type', 'Content-Length',
                                        'Host', 'X-Auth-Key'])


def test_data():
    def request_with_data(data, length=None):
        if length is None:
            length = str(len(data))
        return Request({
            'CONTENT_LENGTH': length,
            'wsgi.input': io.BytesIO(data),
        })

    assert request_with_data(b'').stream.read() == b''
    assert request_with_data(b'abc').stream.read() == b'abc'
    assert request_with_data(b'', 'not an int').stream.read() == b''
    assert request_with_data(b'abc', 'not an int').stream.read() == b'abc'

    request_with_data(b'abc', 'not an int').data() == b''
    assert request_with_data(b'').data() == b''
    req = request_with_data(b'abc')
    assert req.data() == b'abc'
    assert req.data() == b'abc'
    assert request_with_data(b'abc', '2').data() == b'ab'

    with pytest.raises(HTTPException):
        request_with_data(b'').json() == {}
    with pytest.raises(HTTPException):
        request_with_data(b'blah').json()
    assert request_with_data(b'{}').json() == {}
    assert request_with_data(b'{"abc": "def"}').json() == {u'abc': u'def'}


def test_cookies():
    request = Request({
        'HTTP_COOKIE': 'a=b; %FF=%FF',
    })
