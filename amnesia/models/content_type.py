# -*- coding: utf-8 -*-

from amnesia import db

from amnesia.models.root import RootModel

class ContentType(RootModel):

    query = db.Session.query_property()

    def __init__(self, **kwargs):
        super(ContentType, self).__init__(**kwargs)
