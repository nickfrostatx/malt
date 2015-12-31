# -*- coding: utf-8 -*-
"""Test that the package exists and has specified metadata."""

from malt.routing import Router
import pytest


def test_get_and_post():
    router = Router()

    def get_root():
        pass

    def post_root():
        pass

    def get_home():
        pass

    router.add_rule('GET', '/', get_root)
    router.add_rule('POST', '/', post_root)
    router.add_rule('GET', '/home', get_home)
    router.add_rule('GET', '/homie', get_home)

    assert router.path_map == {
        '/': {
            'GET': get_root,
            'POST': post_root,
        },
        '/home': {
            'GET': get_home,
        },
        '/homie': {
            'GET': get_home,
        }
    }

    assert router.view_map == {
        get_root: ('GET', '/'),
        post_root: ('POST', '/'),
        get_home: ('GET', '/home'),
    }

    assert router.get_view('GET', '/') == get_root
    assert router.get_view('POST', '/') == post_root
    assert router.get_view('GET', '/home') == get_home
    assert router.get_view('GET', '/homie') == get_home

    assert router.path_for(get_root) == '/'
    assert router.path_for(post_root) == '/'
    assert router.path_for(get_home) == '/home'


def test_duplicate_route():
    router = Router()

    def get_root():
        pass

    def get_root_again():
        pass

    router.add_rule('GET', '/', get_root)

    for view in (get_root, get_root_again):
        with pytest.raises(Exception) as exc_info:
            router.add_rule('GET', '/', view)
        assert 'Duplicate route: GET /' in str(exc_info)


def test_bad_rules():
    router = Router()

    def get_root():
        pass

    router.add_rule('GET', '/', get_root)

    assert router.get_view('GET', '/') == get_root

    for method in ('GET', 'POST', 'PUT', 'DELETE', 'fake method'):
        with pytest.raises(LookupError) as exc_info:
            router.get_view(method, '/something')
        assert str(exc_info.value) == 'No such path'

    for method in ('POST', 'PUT', 'DELETE', 'fake method'):
        with pytest.raises(LookupError) as exc_info:
            router.get_view(method, '/')
        assert str(exc_info.value) == 'No such method'


def test_missing_view():
    router = Router()

    def get_root():
        pass

    def unregistered():
        pass

    router.add_rule('GET', '/', get_root)

    assert router.path_for(get_root) == '/'

    with pytest.raises(KeyError):
        router.path_for(unregistered)
