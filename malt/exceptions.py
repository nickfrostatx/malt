# -*- coding: utf-8 -*-
"""HTTP exception object."""

from .http import HTTP_STATUS_CODES
from .wrappers import Response


class HTTPException(Exception):

    """This can be raised from middleware to render an error page."""

    def __init__(self, status_code, message=None, exception=None):
        if message is None:
            message = HTTP_STATUS_CODES[status_code]
        super(HTTPException, self).__init__(message)
        self.status_code = status_code
        self.message = message
        self.exception = exception
