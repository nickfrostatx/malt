# -*- coding: utf-8 -*-
"""This module contains the WSGI application object."""

from functools import partial
from .wrappers import Request, Response
import sys


class Malt(object):

    """The application object."""

    def __init__(self):
        self.url_map = {}

    def add_rule(self, method, url, view):
        """Add the """
        if url not in self.url_map:
            self.url_map[url] = {}

        if method in self.url_map[url]:
            raise Exception('Duplicate route: {0} {1}'.format(method, url))

        self.url_map[url][method] = view

        return view

    def method_router(method):
        def route(self, url):
            return partial(self.add_rule, method, url)
        return route

    get = method_router('GET')
    post = method_router('POST')
    put = method_router('PUT')
    delete = method_router('DELETE')
    del method_router

    def dispatch(self, request):
        """Determine the correct view function, and call it."""
        # URL endpoint matching
        try:
            url_rule = self.url_map[request.path]
        except KeyError:
            return Response(b'Not found\n', 404)

        # Method matching
        try:
            view = url_rule[request.method]
        except KeyError:
            return Response(b'Method not allowed\n', 405)

        try:
            response = view(request)
        except:
            return Response(b'Internal server error\n', 500)

        return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        start_response(response.status, response.headers)
        return response

    __call__ = wsgi_app
