# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt import Malt, Request, Response, HTTPException
import pytest


@pytest.fixture
def app():
    app = Malt()

    @app.before_request
    def before(request):
        if request.path == '/before':
            return Response(u'before_request returned\n')

    @app.after_request
    def after(request, response):
        if request.path == '/after':
            return Response(u'after_request returned\n')
        return response

    @app.error_handler
    def handle(error):
        return Response('%s\n' % error.message, code=error.status_code)

    @app.get('/')
    def root(request):
        return Response('Hello World!\n')

    @app.get('/forbidden')
    def forbidden(request):
        raise HTTPException(403, 'Not allowed, man')

    @app.get('/internal')
    def internal(request):
        1/0

    return app


def test_wsgi_exceptions(app):
    arr = [None]

    def start_request(status, headers):
        arr[0] = (status, list(headers))

    requests = [
        ('GET', '/', 200, '200 OK', b'Hello World!\n'),
        ('GET', '/before', 200, '200 OK', b'before_request returned\n'),
        ('GET', '/after', 200, '200 OK', b'after_request returned\n'),
        ('GET', '/forbidden', 403, '403 Forbidden', b'Not allowed, man\n'),
        ('GET', '/asdf', 404, '404 Not Found', b'Not Found\n'),
        ('POST', '/', 405, '405 Method Not Allowed', b'Method Not Allowed\n'),
        ('GET', '/internal', 500, '500 Internal Server Error',
            b'Internal Server Error\n'),
    ]

    for method, url, status_code, status, text in requests:
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': url,
        }

        resp = app.dispatch(Request(environ))
        assert list(resp) == [text]
        assert resp.status_code == status_code
        assert resp.status == status

        for fn in (app.wsgi_app, app):
            assert list(fn(environ, start_request)) == [text]
            assert arr[0] == (status, [('Content-Type',
                                        'text/plain; charset=utf-8')])


def test_dispatch(app):
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
    }

    resp = app.dispatch(Request(environ))
    assert resp.status_code
    assert list(resp) == [b'Hello World!\n']
