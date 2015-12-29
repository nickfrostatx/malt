# -*- coding: utf-8 -*-
"""HTTP exception object."""

from .wrappers import Response


class HTTPException(Response, Exception):

    """This can be raised from middleware to render an error page."""
