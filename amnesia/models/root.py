# -*- coding: utf-8 -*-

from sqlalchemy import orm

class RootModel:

    def __init__(self, **kwargs):
        self.feed(**kwargs)

    def feed(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def format(self, format, **kwargs):
        serializer = Serializer(self)
        return getattr(serializer, format)(**kwargs)
