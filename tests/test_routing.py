# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt import Malt
import pytest


@pytest.fixture
def app():
    app = Malt()

    @app.get('/')
    def root(request):
        return Response('Hello World!\n')

    return app


def test_base_routing():
    app = Malt()

    @app.get('/')
    def root(request):
        return Response('Hello World!\n')

    @app.post('/')
    def post_home(request):
        return Response()

    assert app.router.path_map == {'/': {'GET': root, 'POST': post_home}}


def test_duplicate_route(app):

    def view(request):
        return Response('')

    with pytest.raises(Exception) as exc_info:
        app.get('/')(view)
    assert 'Duplicate route: GET /' in str(exc_info)

    decorator = app.post('/')
    decorator(view)
    with pytest.raises(Exception) as exc_info:
        decorator(view)
    assert 'Duplicate route: POST /' in str(exc_info)


def test_url_for(app):

    @app.get('/hello')
    def hello(request):
        return Response('Hi there\n')

    def unregistered(request):
        return Response('')

    assert app.url_for(hello) == '/hello'
    assert app.url_for(hello, msg='a = b') == '/hello?msg=a+%3D+b'

    with pytest.raises(Exception) as exc_info:
        app.url_for(unregistered)
    assert 'is not registered to a url' in str(exc_info)
