# -*- coding: utf-8 -*-
"""This module contains the WSGI application object."""

from functools import partial
from .exceptions import HTTPException
from .routing import Router
from .wrappers import Request, Response
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class Malt(object):

    """The application object."""

    def __init__(self):
        self.router = Router()
        self._error_handler = self.default_error_handler
        self._before_request = []
        self._after_request = []

    def url_for(self, view, **params):
        """Return the url for a particular view function."""
        url = self.router.path_for(view)
        if params:
            url += '?' + urlencode(params)
        return url

    def method_router(method):
        def route(self, url):
            def add(fn):
                self.router.add_rule(method, url, fn)
                return fn
            return add
        return route

    get = method_router('GET')
    post = method_router('POST')
    put = method_router('PUT')
    delete = method_router('DELETE')
    del method_router

    def default_error_handler(self, exception):
        html = '''<!doctype html>
<html>
<head><title>{status_code} {message}</title></head>
<body>
<center><h1>{status_code} {message}</h1></center>
</body>
</html>
'''.format(status_code=exception.status_code, message=exception.message)
        return Response(html, code=exception.status_code, mimetype='text/html')

    def error_handler(self, fn):
        """Register a new error handler, replacing the existing one."""
        self._error_handler = fn
        return fn

    def handle_error(self, error):
        if not isinstance(error, HTTPException):
            error = HTTPException(exception=error)
        try:
            response = self._error_handler(error)
        except Exception as exc:
            response = self.default_error_handler(HTTPException(exception=exc))
        return response

    def before_request(self, fn):
        self._before_request.append(fn)

    def after_request(self, fn):
        self._after_request.append(fn)

    def call_view(self, request):
        """Determine the correct view function, and call it."""
        # URL endpoint matching
        try:
            view = self.router.get_view(request.method, request.path)
        except LookupError as exc:
            if exc.args[0] == 'No such path':
                raise HTTPException(404, exception=exc)
            elif exc.args[0] == 'No such method':
                raise HTTPException(405, exception=exc)
            else:
                raise
        return view(request)

    def get_response(self, fn, *args):
        """Call fn using args. Handle any errors."""
        try:
            response = fn(*args)
        except Exception as exc:
            response = self.handle_error(exc)
        return response

    def dispatch(self, request):
        for fn in self._before_request:
            response = self.get_response(fn, request)
            if response is not None:
                break
        else:
            response = self.get_response(self.call_view, request)
        for fn in self._after_request:
            response = self.get_response(fn, request, response)
        return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        start_response(response.status, list(response.headers))
        return response

    __call__ = wsgi_app
