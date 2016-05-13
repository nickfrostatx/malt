# -*- coding: utf-8 -*-
"""WSGI wrapper objects."""

from .exceptions import HTTPException
from .helpers import is_string, want_bytes, want_text
from .http import HTTP_STATUS_CODES, MIME_PLAIN
import json


class EnvironHeaders(object):

    """Read the headers from environ."""

    def __init__(self, environ):
        self.environ = environ

    def __getitem__(self, header):
        """Convert to WSGI naming scheme.

        'X-Forwarded-For' returns the value of HTTP_X_FORWARDED_FOR
        """
        try:
            key = header.upper().replace('-', '_')
            # Content-Type and Content-Length are in the environ
            if key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                value = self.environ[key]
            else:
                value = self.environ['HTTP_' + key]
            return want_text(value, charset='latin1', errors='replace')
        except KeyError:
            # Use the original header key in the exception message
            raise KeyError(header)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    def __iter__(self):
        """Iterate through header keys (same behavior as a dict)."""
        for env_key in self.environ:
            if env_key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = env_key
            elif env_key.startswith('HTTP_'):
                key = env_key[5:]
            else:
                continue
            yield '-'.join(part.capitalize() for part in key.split('_'))

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
    [(b'X-Abc', b'apple')]
    >>> headers['X-Green] = ['eggs', 'spam']
    >>> list(headers)
    [(b'X-Abc', b'apple'), (b'X-Green', b'eggs'), (b'X-Green', b'spam')]
    """

    def __init__(self):
        self._headers = {}
        self._order = []

    def _key_for(self, key):
        return want_bytes(key.upper(), 'latin1')

    def _ensure_contains(self, header):
        """Raise a KeyError if the given header does not exist."""
        if self._key_for(header) not in self._headers:
            raise KeyError(header)

    def __getitem__(self, header):
        """Return the first vaue for the given header."""
        self._ensure_contains(header)

        values = self._headers[self._key_for(header)]
        return values[0]

    def __setitem__(self, header, value):
        """Value may be either a string, or an iterable of strings."""
        if is_string(value):
            value = [value]

        if self._key_for(header) not in self._headers:
            self._order.append(header)
        self._headers[self._key_for(header)] = value

    def add(self, header, value):
        """Add a new key-value pair, without overwriting."""
        if not is_string(value):
            raise TypeError('Headers.add does not expect a list')

        if self._key_for(header) not in self._headers:
            self._order.append(header)
            self._headers[self._key_for(header)] = []
        self._headers[self._key_for(header)].append(value)

    def __delitem__(self, header):
        """Remove the header from the dict, and from the order list."""
        self._ensure_contains(header)

        header_key = self._key_for(header)
        del self._headers[header_key]
        self._order = [key for key in self._order
                       if self._key_for(key) != header_key]

    def __iter__(self):
        """Yield each header-value pair."""
        for header in self._order:
            for value in self._headers[self._key_for(header)]:
                header_enc = want_bytes(header, 'latin1')
                value_enc = want_bytes(value, 'latin1')
                yield header_enc, value_enc


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

    charset = 'utf-8'

    method = environ_property('REQUEST_METHOD')
    path = environ_property('PATH_INFO')
    script_name = environ_property('SCRIPT_NAME')
    host = environ_property('SERVER_NAME')
    port = environ_property('SERVER_PORT')
    scheme = environ_property('wsgi.url_scheme')
    protocol = environ_property('SERVER_PROTOCOL')
    remote_addr = environ_property('REMOTE_ADDR')
    query_string = environ_property('QUERY_STRING')
    stream = environ_property('wsgi.input')
    del environ_property

    @property
    def raw(self):
        content_type = self.headers.get('Content-Length')
        if content_type:
            try:
                size = int(content_type)
            except ValueError:
                raise HTTPException(400)
            return self.stream.read(size)
        return b''

    @property
    def json(self):
        content_type = self.headers.get('Content-Type', '')
        prefix = 'application/json; charset='
        if content_type.startswith(prefix):
            self.charset = content_type[len(prefix):]
        try:
            return json.loads(self.raw.decode(self.charset))
        except ValueError:
            raise HTTPException(400)

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

    def __init__(self, data='', code=200, mimetype=MIME_PLAIN,
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
            yield want_bytes(chunk, charset=self.charset)
