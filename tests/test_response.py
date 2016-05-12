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
    response = list(Response(u'böse', charset='latin')) == [b'b\xf6se']

    with pytest.raises(UnicodeEncodeError):
        list(Response(u'こんにちは', charset='latin'))

    assert list(Response(u'こんにちは', charset='euc-jp')) == [
        b'\xa4\xb3\xa4\xf3\xa4\xcb\xa4\xc1\xa4\xcf']


def test_response_headers():
    response = Response()
    assert list(response.headers) == [('Content-Type',
                                       'text/plain; charset=utf-8')]
    response.headers['X-Powered-By'] = ['Coffee', 'Ramen']
    assert list(response.headers) == [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('X-Powered-By', 'Coffee'), ('X-Powered-By', 'Ramen')]

    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.headers['X-Powered-By'] == 'Coffee'

    del response.headers['x-powered-by']
    for key in ('X-Powered-By', 'X-Abc'):
        with pytest.raises(KeyError) as exc_info:
            response.headers[key]
        assert exc_info.value.args[0] == key

    response.headers.add('X-Snoop-Options', 'nosnoop')
    response.headers.add('Set-Cookie', 'a=b')
    response.headers.add('set-cookie', 'c=d')
    assert list(response.headers) == [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('X-Snoop-Options', 'nosnoop'),
        ('Set-Cookie', 'a=b'), ('Set-Cookie', 'c=d')]
