# -*- coding: utf-8 -*-
"""This module contains the WSGI application object."""

from functools import partial
from .exceptions import HTTPException
from .wrappers import Request, Response
import sys
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class Malt(object):

    """The application object."""

    def __init__(self):
        self.url_map = {}
        self.view_map = {}

    def add_rule(self, method, url, view):
        """Add the """
        if url not in self.url_map:
            self.url_map[url] = {}

        if method in self.url_map[url]:
            raise Exception('Duplicate route: {0} {1}'.format(method, url))

        self.url_map[url][method] = view
        self.view_map[view] = url

        return view

    def url_for(self, view, **params):
        """Return the url for a particular view function."""
        if view not in self.view_map:
            raise Exception('The view %r is not registered to a url' % view)
        url = self.view_map[view]
        if params:
            url += '?' + urlencode(params)
        return url

    def method_router(method):
        def route(self, url):
            return partial(self.add_rule, method, url)
        return route

    get = method_router('GET')
    post = method_router('POST')
    put = method_router('PUT')
    delete = method_router('DELETE')
    del method_router

    def handle_error(self, exc):
        return Response('%s\n' % exc.message, code=exc.status_code)

    def dispatch(self, request):
        """Determine the correct view function, and call it."""
        # URL endpoint matching
        try:
            url_rule = self.url_map[request.path]
        except KeyError:
            return self.handle_error(HTTPException(404))

        # Method matching
        try:
            view = url_rule[request.method]
        except KeyError:
            return self.handle_error(HTTPException(405))

        try:
            return view(request)
        except HTTPException as exc:
            return self.handle_error(exc)
        except:
            return self.handle_error(HTTPException(500))

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        start_response(response.status, list(response.headers))
        return response

    __call__ = wsgi_app
