# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt import Malt, Request, Response, HTTPException, json as jsonify
import json
import pytest


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


@app.get('^/$')
def root(request):
    return Response('Hello World!\n')


@app.get('^/forbidden$')
def forbidden(request):
    raise HTTPException(403, 'Not allowed, man')


@app.get('^/things/(\d+)$')
def thing(request, thing_id):
    thing_id = int(thing_id)
    return Response('Thing {0:d}\n'.format(thing_id))


@app.get('^/internal$')
def internal(request):
    1/0


def not_a_view():
    pass


def test_wsgi_exceptions():
    wsgi = app.wsgi_app({})

    arr = [None]

    def start_request(status, headers):
        arr[0] = (status, list(headers))

    requests = [
        ('GET', '/', 200, '200 OK', b'Hello World!\n'),
        ('GET', '/before', 200, '200 OK', b'before_request returned\n'),
        ('GET', '/after', 200, '200 OK', b'after_request returned\n'),
        ('GET', '/forbidden', 403, '403 Forbidden', b'Not allowed, man\n'),
        ('GET', '/things/50', 200, '200 OK', b'Thing 50\n'),
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

        resp = app.dispatch(Request(environ, {}))
        assert list(resp) == [text]
        assert resp.status_code == status_code
        assert resp.status == status

        assert list(wsgi(environ, start_request)) == [text]
        assert arr[0] == (status, [('Content-Type',
                                    'text/plain; charset=utf-8')])


def test_url_for():
    assert app.url_for(internal) == r'^/internal$'

    with pytest.raises(KeyError):
        app.url_for(not_a_view)


def test_dispatch_error(monkeypatch):
    def raises_lookup_error(method, path):
        raise LookupError('Some unexpected message')

    monkeypatch.setattr(app.router, 'get_view', raises_lookup_error)

    req = Request({
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/'
    }, {})
    resp = app.dispatch(req)
    assert list(resp) == [b'Internal Server Error\n']
    assert resp.status_code == 500
    assert resp.status == '500 Internal Server Error'


def test_config():
    a = Malt()

    @a.get('/')
    def dump_config(request):
        return jsonify(request.config)

    wsgi = a.wsgi_app({'a': 'b'})

    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
    }
    rv = wsgi(environ, lambda status, headers: None)
    rv_text = next(iter(rv)).decode('utf-8')
    assert json.loads(rv_text)['a'] == 'b'


def test_sessions():
    a = Malt()

    @a.get('/')
    def dump_session(request):
        old_sess = dict(request.session)
        request.session['a'] = 2
        return jsonify(old_sess)

    wsgi = a.wsgi_app({'SESSIONS': True, 'SECRET_KEY': 'abc'})

    # Capture response headers
    headers = [None]

    def start_response(_, h):
        headers[0] = h

    # Send with a valid session
    session_token = 'eyJhIjoxfQ.2XFQKMS-erhoKkSGsezDxFsim6YctUnzxaiiMP1wzFs'
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'HTTP_COOKIE': 'session=' + session_token,
    }

    rv = wsgi(environ, start_response)

    rv_text = next(iter(rv)).decode('utf-8')
    assert json.loads(rv_text) == {'a': 1}

    # Check response session cookie
    set_cookie = next(v for k, v in headers[0] if k.lower() == 'set-cookie')
    expected = 'eyJhIjoyfQ.WW2DtOr1pkaM9nrC9sw2kHW3Cxd57hDhLie--g46DjE'
    assert set_cookie == 'session=' + expected
