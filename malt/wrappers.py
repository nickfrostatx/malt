# -*- coding: utf-8 -*-
"""WSGI wrapper objects."""

from functools import partial
from .http import HTTP_STATUS_CODES


class EnvironHeaders(object):

    """Read the headers from a """

    def __init__(self, environ):
        self.environ = environ

    def __getitem__(self, header):
        """Convert to WSGI naming scheme.

        For example, X-Forwarded-For becomes HTTP_X_FORWARDED_FOR
        """
        try:
            key = header.upper().replace('-', '_')
            # Content-Type and Content-Length are in the environ
            if key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                return self.environ[key]
            return self.environ['HTTP_' + key]
        except KeyError:
            # Use the original header key in the exception message
            raise KeyError(header)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


def environ_property(key, default=None):
    @property
    def getter(self):
        return self.environ.get(key, default)
    return getter


class Request(object):

    """WSGI request wrapper."""

    def __init__(self, environ):
        self.environ = environ
        self.headers = EnvironHeaders(environ)

    method = environ_property('REQUEST_METHOD')
    path = environ_property('PATH_INFO')
    script_name = environ_property('SCRIPT_NAME')
    host = environ_property('SERVER_NAME')
    port = environ_property('SERVER_PORT')
    scheme = environ_property('wsgi.url_scheme')
    protocol = environ_property('SERVER_PROTOCOL')
    query_string = environ_property('QUERY_STRING')

    @property
    def url(self):
        url = self.scheme + '://'
        if self.headers.get('Host'):
            url += self.headers.get('Host')
        else:
            url += self.host
            if self.port != ('80' if self.scheme == 'http' else '443'):
                url += ':' + self.port
        url += self.script_name + self.path
        if self.query_string:
            url += '?' + self.query_string
        return url


class Response(object):

    """WSGI response object."""

    def __init__(self, data, code=200):
        self.data = data
        self.status_code = code
        self.headers = []

    def _get_status_code(self):
        return self._status_code

    def _set_status_code(self, code):
        try:
            self.status = '{0:d} {1}'.format(code, HTTP_STATUS_CODES[code])
        except (KeyError, ValueError):
            raise ValueError('Invalid status: {0!r}'.format(code))
        self._status_code = code

    status_code = property(_get_status_code, _set_status_code)
    del _get_status_code, _set_status_code

    def __iter__(self):
        data = self.data
        if isinstance(data, type(u'')):
            data = data.encode('utf-8')
        yield data
