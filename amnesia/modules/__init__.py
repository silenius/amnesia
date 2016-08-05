# -*- coding: utf-8 -*-

from sqlalchemy import orm

class Base:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feed(**kwargs)

    def feed(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)
