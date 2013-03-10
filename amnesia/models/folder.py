# -*- coding: utf-8 -*-

from amnesia import db
from amnesia.models import content


class FolderQuery(content.ContentQuery):

    def ___init__(self, *args, **kwargs):
        super(FolderQuery, self).__init__(*args, **kwargs)


class Folder(content.Content):

    query = db.Session.query_property(FolderQuery)

    def __init__(self, **kwargs):
        super(Folder, self).__init__(**kwargs)
