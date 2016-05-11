Malt
===============================

.. image:: https://img.shields.io/travis/nickfrostatx/malt.svg
    :target: https://travis-ci.org/nickfrostatx/malt

.. image:: https://img.shields.io/coveralls/nickfrostatx/malt.svg
    :target: https://coveralls.io/github/nickfrostatx/malt

.. image:: https://img.shields.io/pypi/v/malt.svg
    :target: https://pypi.python.org/pypi/malt

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/nickfrostatx/malt/master/LICENSE

My toy WSGI microframework.

This is very much a work in progress, it's not ready to use just yet.

Heavily inspired by (or stolen from) Flask/Werkzeug.

Installation
------------

This will run on Python 2.6+ or 3.3+. There are no dependencies.

.. code-block:: bash

    $ pip install malt

Usage
-----

.. code-block:: python

    from malt import Malt, Response

    app = Malt()

    @app.get('/')
    def home(request):
        return Response('Hello world')
