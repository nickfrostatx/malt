# -*- coding: utf-8 -*-
"""This module contains the WSGI application object."""

from .exceptions import HTTPException
from .http import MIME_HTML
from .models import Request, Response
from .routing import Router
from .sessions import open_session, save_session
import traceback
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

    def url_for(self, view):
        """Return the url for a particular view function."""
        url = self.router.path_for(view)
        return url

    def method_router(method):
        def route(self, url):
            def add(fn):
                self.router.add_rule(method, url, fn)
                return fn
            return add
        return route

    get = method_router('GET')
    patch = method_router('PATCH')
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
        return Response(html, code=exception.status_code, mimetype=MIME_HTML)

    def error_handler(self, fn):
        """Register a new error handler, replacing the existing one."""
        self._error_handler = fn
        return fn

    def handle_error(self, error):
        if not isinstance(error, HTTPException):
            traceback.print_exc()
            error = HTTPException(exception=error)
        try:
            response = self._error_handler(error)
        except Exception as exc:
            response = self.default_error_handler(HTTPException(exception=exc))
        return response

    # Session handling functions
    open_session = staticmethod(open_session)
    save_session = staticmethod(save_session)

    def before_request(self, fn):
        self._before_request.append(fn)

    def after_request(self, fn):
        self._after_request.append(fn)

    def call_view(self, request):
        """Determine the correct view function, and call it."""
        # URL endpoint matching
        try:
            view, args = self.router.get_view(request.method, request.path)
        except LookupError as exc:
            if exc.args[0] == 'No such path':
                raise HTTPException(404, exception=exc)
            elif exc.args[0] == 'No such method':
                raise HTTPException(405, exception=exc)
            else:
                raise
        return view(request, *args)

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

    def wsgi_app(self, config):
        def callable(environ, start_response):
            use_sessions = config.get('SESSIONS', False)
            request = Request(environ, dict(config))
            if use_sessions:
                request.session = self.open_session(request)
            response = self.dispatch(request)
            if use_sessions:
                self.save_session(request, response)
            start_response(response.status, list(response.headers))
            return response
        return callable
