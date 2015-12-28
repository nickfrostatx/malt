# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt import Malt, Request, Response
import pytest


@pytest.fixture
def app():
    app = Malt()

    @app.get('/')
    def root(request):
        return Response('Hello World!\n')

    @app.get('/internal')
    def internal(request):
        1/0

    return app


def test_dispatch(app):
    for method, url, status, text in [
        ('GET', '/', 200, 'Hello World!\n'),
        ('GET', '/asdf', 404, b'Not found\n'),
        ('POST', '/', 405, b'Method not allowed\n'),
        ('GET', '/internal', 500, b'Internal server error\n'),
    ]:
        request = Request({
            'REQUEST_METHOD': method,
            'PATH_INFO': url,
        })

        resp = app.dispatch(request)
        assert resp.status_code == status
        assert resp.response == [text]


def test_wsgi(app):
    arr = [None]

    def start_request(status, headers):
        arr[0] = (status, headers)

    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
    }

    for fn in (app.wsgi_app, app):
        assert list(fn(environ, start_request)) == [b'Hello World!\n']
        assert arr[0] == ('200 OK', [])


def test_duplicate_route(app):
    with pytest.raises(Exception) as exc_info:
        app.get('/')(lambda x: x)
    assert 'Duplicate route: GET /' in str(exc_info)

    decorator = app.post('/')
    decorator(lambda x: x)
    with pytest.raises(Exception) as exc_info:
        decorator(lambda x: x)
    assert 'Duplicate route: POST /' in str(exc_info)
