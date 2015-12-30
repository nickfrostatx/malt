# -*- coding: utf-8 -*-
"""The URL routing."""


class Router(object):

    """Connect view functions to URL rules."""

    def __init__(self):
        self.path_map = {}
        self.view_map = {}

    def add_rule(self, method, path, view):
        self.path_map.setdefault(path, {})
        rule = self.path_map[path]
        if method in rule:
            raise Exception('Duplicate route: {0} {1}'.format(method, path))
        rule[method] = view
        self.view_map[view] = method, path

    def get_view(self, method, path):
        if path not in self.path_map:
            raise LookupError('No such path')
        if method not in self.path_map[path]:
            raise LookupError('No such method')
        return self.path_map[path][method]

    def path_for(self, view):
        try:
            method, path = self.view_map[view]
            return path
        except KeyError:
            raise Exception('The view %r is not registered to a url' % view)
