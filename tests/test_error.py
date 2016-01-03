# -*- coding: utf-8 -*-
"""Test that app.get_response pretty much always returns a response.."""

from malt import Malt, Request, Response
from malt.exceptions import HTTPException
import pytest


def test_default_handler():
    app = Malt()

    def divide(a, b):
        return a / b

    def raise_exc(status=None, msg=None):
        raise HTTPException(status, msg)

    for args in ((divide, 1, 0),
                 (raise_exc,),
                 (raise_exc, -1),
                 (raise_exc, 418.),
                 (raise_exc, 500)):
        response = app.get_response(*args)
        assert '<h1>500 Internal Server Error</h1>' in response.response[0]

    response = app.get_response(raise_exc, 418)
    assert '<h1>418 I\'m a teapot</h1>' in response.response[0]

    response = app.get_response(raise_exc, 418, 'Good Stuff')
    assert '<h1>418 Good Stuff</h1>' in response.response[0]

    response = app.get_response(raise_exc, 418., 'Bad Stuff')
    assert '<h1>500 Bad Stuff</h1>' in response.response[0]

    response = app.get_response(raise_exc, -1, 'Worse Stuff')
    assert '<h1>500 Worse Stuff</h1>' in response.response[0]


def test_custom_handler():
    app = Malt()

    @app.error_handler
    def handle(exc):
        return Response('%d\n%s' % (exc.status_code, exc.message),
                        code=exc.status_code)

    def divide(a, b):
        return a / b

    def raise_exc(status=None, msg=None):
        raise HTTPException(status, msg)

    for args in ((divide, 1, 0),
                 (raise_exc,),
                 (raise_exc, -1),
                 (raise_exc, 418.),
                 (raise_exc, 500)):
        response = app.get_response(*args)
        assert '500\nInternal Server Error' in response.response[0]

    response = app.get_response(raise_exc, 418)
    assert '418\nI\'m a teapot' in response.response[0]

    response = app.get_response(raise_exc, 418, 'Good Stuff')
    assert '418\nGood Stuff' in response.response[0]

    response = app.get_response(raise_exc, 418., 'Bad Stuff')
    assert '500\nBad Stuff' in response.response[0]

    response = app.get_response(raise_exc, -1, 'Worse Stuff')
    assert '500\nWorse Stuff' in response.response[0]


def test_bad_custom_handler():
    app = Malt()

    @app.error_handler
    def dont_actually_handle(exc):
        raise exc

    def divide(a, b):
        return a / b

    def raise_exc(status=None, msg=None):
        raise HTTPException(status, msg)

    for args in ((divide, 1, 0),
                 (raise_exc,),
                 (raise_exc, -1),
                 (raise_exc, 418.),
                 (raise_exc, 500),
                 (raise_exc, 418),
                 (raise_exc, 418, 'Good Stuff'),
                 (raise_exc, 418., 'Bad Stuff'),
                 (raise_exc, -1, 'Worse Stuff')):
        response = app.get_response(*args)
        assert '<h1>500 Internal Server Error</h1>' in response.response[0]


def test_error_in_response():
    """A response that errors when iterated should still get returned.

    We'll let the WSGI server deal with errors mid-way through iterating
    through a response object.
    """
    app = Malt()

    def secretly_bad_response():
        def gen():
            for i in range(10):
                if i == 9:
                    raise Exception()
                yield str(i)

        return Response(gen())

    response = app.get_response(secretly_bad_response)
    with pytest.raises(Exception):
        list(response)
