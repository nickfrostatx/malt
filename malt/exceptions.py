# -*- coding: utf-8 -*-
"""HTTP exception object."""

from .http import HTTP_STATUS_CODES


class HTTPException(Exception):

    """This can be raised from middleware to render an error page."""

    def __init__(self, code=None, message=None, exception=None):
        if not isinstance(code, int) or code not in HTTP_STATUS_CODES:
            code = 500
        if message is None:
            message = HTTP_STATUS_CODES[code]
        super(HTTPException, self).__init__(message)
        self.status_code = code
        self.message = message
        self.exception = exception
