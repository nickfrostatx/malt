# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt import Malt, Request, Response, HTTPException
import pytest


@pytest.fixture
def app():
    app = Malt()

    @app.get('/')
    def root(request):
        return Response('Hello World!\n')

    @app.get('/forbidden')
    def forbidden(request):
        raise HTTPException('Forbidden\n', code=403)

    @app.get('/internal')
    def internal(request):
        1/0

    return app


requests = [
    ('GET', '/forbidden', 403, '403 Forbidden', b'Forbidden\n'),
    ('GET', '/asdf', 404, '404 Not Found', b'Not found\n'),
    ('POST', '/', 405, '405 Method Not Allowed', b'Method not allowed\n'),
    ('GET', '/internal', 500, '500 Internal Server Error',
        b'Internal server error\n'),
]


def test_wsgi_exceptions(app):
    arr = [None]

    def start_request(status, headers):
        arr[0] = (status, list(headers))

    for method, url, status_code, status, text in requests:
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': url,
        }

        with pytest.raises(HTTPException) as exc_info:
            app.dispatch(Request(environ))
        resp = exc_info.value
        assert resp.status_code == status_code
        assert resp.status == status
        assert list(resp) == [text]

        for fn in (app.wsgi_app, app):
            assert list(fn(environ, start_request)) == [text]
            assert arr[0] == (status, [('Content-Type', 'text/plain')])


def test_dispatch(app):
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
    }

    resp = app.dispatch(Request(environ))
    assert resp.status_code
    assert list(resp) == [b'Hello World!\n']
