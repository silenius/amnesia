# -*- coding: utf-8 -*-

import logging

import venusian

log = logging.getLogger(__name__)


class widget_config:

    def __init__(self, name):
        self.name = name

    def register(self, scanner, name, wrapped):
        registry = scanner.config.registry
        widgets = registry.setdefault('widgets', {})
        widgets[self.name] = wrapped

    def __call__(self, wrapped):
        venusian.attach(wrapped, self.register)
        return wrapped
