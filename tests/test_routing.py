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

    assert app.url_map == {'/': {'GET': root}}


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

    with pytest.raises(Exception) as exc_info:
        app.add_rule('GET', '/', view)
    assert 'Duplicate route: GET /' in str(exc_info)
