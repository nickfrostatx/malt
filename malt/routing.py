# -*- coding: utf-8 -*-
"""The URL routing.

This module implements regex-based URL view matching.
"""
import re


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
        reg = re.compile(path)
        self.path_map.setdefault(reg, {})

        rule = self.path_map[reg]
        if method in rule:
            raise Exception('Duplicate route: {0} {1}'.format(method, path))
        rule[method] = view
        if view not in self.view_map:
            self.view_map[view] = method, path

    def get_view(self, method, path):
        """Look up the view."""
        for reg, rule in self.path_map.items():
            m = reg.match(path)
            if m is not None:
                if method not in rule:
                    raise LookupError('No such method')
                view = rule[method]
                args = m.groups()
                return view, args
        raise LookupError('No such path')

    def path_for(self, view):
        _, path = self.view_map[view]
        return path
