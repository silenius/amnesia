# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

class Base:

    def __init__(self, **kwargs):
        self.feed(**kwargs)

    def feed(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)
