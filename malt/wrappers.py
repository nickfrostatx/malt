# -*- coding: utf-8 -*-
"""WSGI wrapper objects."""

from functools import partial
from .http import HTTP_STATUS_CODES
from .util import is_text


class EnvironHeaders(object):

    """Read the headers from environ."""

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


class Headers(object):

    """Header data structure.

    An appropriate description would be an ordered multi-dict.

    >>> headers = Headers()
    >>> headers['X-Abc'] = 'apple'
    >>> list(headers)
    [('X-Abc', 'apple')]
    >>> headers['X-Green] = ['eggs', 'spam']
    >>> list(headers)
    [('X-Abc', 'apple'), ('X-Green', 'eggs'), ('X-Green', 'spam')]
    """

    def __init__(self):
        self._headers = {}
        self._order = []

    def _ensure_contains(self, header):
        """Raise a KeyError if the given header does not exist."""
        if header.upper() not in self._headers:
            raise KeyError(header)

    def __getitem__(self, header):
        """Return the first vaue for the given header."""
        self._ensure_contains(header)

        values = self._headers[header.upper()]
        return values[0]

    def __setitem__(self, header, value):
        """Value may be either a string, or an iterable of strings."""
        if is_text(value):
            value = [value]

        if header.upper() not in self._headers:
            self._order.append(header)
        self._headers[header.upper()] = value

    def __delitem__(self, header):
        """Remove the header from the dict, and from the order list."""
        self._ensure_contains(header)

        header_key = header.upper()
        del self._headers[header_key]
        self._order = [key for key in self._order if key.upper != header_key]

    def __iter__(self):
        """Yield each header-value pair."""
        for header in self._order:
            for value in self._headers[header.upper()]:
                yield header, value


class Request(object):

    """WSGI request wrapper."""

    def __init__(self, environ):
        self.environ = environ
        self.headers = EnvironHeaders(environ)

    def environ_property(key):
        @property
        def get_property(self):
            return self.environ.get(key)
        return get_property

    method = environ_property('REQUEST_METHOD')
    path = environ_property('PATH_INFO')
    script_name = environ_property('SCRIPT_NAME')
    host = environ_property('SERVER_NAME')
    port = environ_property('SERVER_PORT')
    scheme = environ_property('wsgi.url_scheme')
    protocol = environ_property('SERVER_PROTOCOL')
    query_string = environ_property('QUERY_STRING')
    del environ_property

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

    def __init__(self, data='', code=200, mimetype='text/plain',
                 charset='utf-8'):
        if isinstance(data, (bytes, type(u''))):
            self.response = [data]
        else:
            self.response = data
        self.status_code = code
        self.charset = charset
        self.headers = Headers()
        self.headers['Content-Type'] = mimetype

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
        for chunk in self.response:
            if isinstance(chunk, type(u'')):
                yield chunk.encode(self.charset)
            else:
                yield chunk
