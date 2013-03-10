# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia import db

class RootQuery(orm.Query):

    def __init__(self, *args, **kwargs):
        super(RootQuery, self).__init__(*args, **kwargs)

class RootModel(object):

    query = db.Session.query_property(RootQuery)

    def __init__(self, **kwargs):
        super(RootModel, self).__init__(**kwargs)
        self.feed(**kwargs)

    def feed(self, **kwargs):
        for (key, value) in kwargs.iteritems():
            setattr(self, key, value)
