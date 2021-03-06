# -*- coding: utf-8 -*-
"""Test the request wrapper."""

from malt import Response
import pytest


def test_status_code():
    assert Response('').status_code == 200
    assert Response('', 418).status_code == 418


def test_status_text():
    assert Response().status == '200 OK'
    assert Response(code=100).status == '100 Continue'
    assert Response(code=418).status == '418 I\'m a teapot'


def test_status_invalid():
    with pytest.raises(ValueError) as exc:
        Response(code=200.)
    assert 'Invalid status: 200.0' in str(exc)

    for code in (100., '', '200', -15, 0, 199, 600):
        with pytest.raises(ValueError) as exc:
            Response().status_code = code
        assert 'Invalid status: ' + repr(code) in str(exc)


def test_response_iterable():
    assert Response('abc').response == ['abc']
    assert Response([b'abc', 'déf']).response == [b'abc', 'déf']


def test_response_text():
    assert list(Response(b'Some text')) == [b'Some text']
    assert list(Response(u'Some text')) == [b'Some text']
    assert list(Response([b'abc', 'déf'])) == [b'abc', b'd\xc3\xa9f']


def test_unicode_response():
    assert list(Response(u'こんにちは')) == [
        b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf']


def test_alternate_charsets():
    assert list(Response(u'böse', charset='latin')) == [b'b\xf6se']

    with pytest.raises(UnicodeEncodeError):
        list(Response(u'こんにちは', charset='latin'))

    assert list(Response(u'こんにちは', charset='euc-jp')) == [
        b'\xa4\xb3\xa4\xf3\xa4\xcb\xa4\xc1\xa4\xcf']


def test_response_headers():
    response = Response()
    assert list(response.headers) == [('Content-Type',
                                       'text/plain; charset=utf-8')]
    response.headers[u'X-Powered-By'] = [b'Coffee', u'Ramen']
    assert list(response.headers) == [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('X-Powered-By', 'Coffee'), ('X-Powered-By', 'Ramen')]

    assert response.headers[u'Content-Type'] == u'text/plain; charset=utf-8'
    assert response.headers[u'X-Powered-By'] == b'Coffee'

    del response.headers[b'x-powered-by']
    for key in (u'X-Powered-By', u'X-Abc'):
        with pytest.raises(KeyError) as exc_info:
            response.headers[key]
        assert exc_info.value.args[0] == key

    response.headers.add(u'X-Snoop-Options', u'nosnoop')
    response.headers.add(b'Set-Cookie', u'a=b')
    response.headers.add(u'set-cookie', b'c=d')
    assert list(response.headers) == [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('X-Snoop-Options', 'nosnoop'),
        ('Set-Cookie', 'a=b'), ('Set-Cookie', 'c=d')]

    with pytest.raises(TypeError) as exc_info:
        response.headers.add(u'Set-Cookie', ['abc'])
    assert exc_info.value.args[0] == 'Headers.add does not expect a list'


def test_set_cookie():
    response = Response()
    assert list(response.headers) == [('Content-Type',
                                       'text/plain; charset=utf-8')]

    response.set_cookie(u'a', u'1')
    response.set_cookie('b', '2')
    response.set_cookie('empty_value', '')
    response.set_cookie('key_only')
    assert list(response.headers)[1:] == [
        ('Set-Cookie', 'a=1'),
        ('Set-Cookie', 'b=2'),
        ('Set-Cookie', 'empty_value='),
        ('Set-Cookie', 'key_only'),
    ]
