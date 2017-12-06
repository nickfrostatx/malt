# -*- coding: utf-8 -*-
"""Test the router."""

from malt.routing import Router
import pytest
import re


def test_get_and_post():
    router = Router()

    def get_root():
        pass

    def post_root():
        pass

    def get_home():
        pass

    def get_thing(t):
        pass

    router.add_rule('GET', r'^/$', get_root)
    router.add_rule('POST', r'^/$', post_root)
    router.add_rule('GET', r'^/home$', get_home)
    router.add_rule('GET', r'^/homie$', get_home)
    router.add_rule('GET', r'^/things/(\d+)$', get_thing)

    assert router.path_map == {
        re.compile(r'^/$'): {
            'GET': get_root,
            'POST': post_root,
        },
        re.compile(r'^/home$'): {
            'GET': get_home,
        },
        re.compile(r'^/homie$'): {
            'GET': get_home,
        },
        re.compile(r'^/things/(\d+)$'): {
            'GET': get_thing,
        },
    }

    assert router.view_map == {
        get_root: ('GET', r'^/$'),
        post_root: ('POST', r'^/$'),
        get_home: ('GET', r'^/home$'),
        get_thing: ('GET', r'^/things/(\d+)$'),
    }

    assert router.get_view('GET', '/') == (get_root, ())
    assert router.get_view('POST', '/') == (post_root, ())
    assert router.get_view('GET', '/home') == (get_home, ())
    assert router.get_view('GET', '/homie') == (get_home, ())
    assert router.get_view('GET', '/things/123') == (get_thing, ('123',))

    assert router.path_for(get_root) == r'^/$'
    assert router.path_for(post_root) == r'^/$'
    assert router.path_for(get_home) == '^/home$'


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

    router.add_rule('GET', '^/$', get_root)

    assert router.get_view('GET', '/') == (get_root, ())

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

    router.add_rule('GET', r'^/$', get_root)

    assert router.path_for(get_root) == r'^/$'

    with pytest.raises(KeyError):
        router.path_for(unregistered)
