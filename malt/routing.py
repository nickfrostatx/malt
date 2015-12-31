# -*- coding: utf-8 -*-
"""The URL routing."""


class Router(object):

    """Connect view functions to URL rules."""

    def __init__(self):
        self.path_map = {}
        self.view_map = {}

    def add_rule(self, method, path, view):
        """Store the view and rule relation in the two lookup maps.

        The view gets stored under the path and method in the path_map
        matrix. The path/method rule is stored under view in view_map.
        """
        self.path_map.setdefault(path, {})
        rule = self.path_map[path]
        if method in rule:
            raise Exception('Duplicate route: {0} {1}'.format(method, path))
        rule[method] = view
        if view not in self.view_map:
            self.view_map[view] = method, path

    def get_view(self, method, path):
        """Look up the view """
        if path not in self.path_map:
            raise LookupError('No such path')
        if method not in self.path_map[path]:
            raise LookupError('No such method')
        return self.path_map[path][method]

    def path_for(self, view):
        method, path = self.view_map[view]
        return path
