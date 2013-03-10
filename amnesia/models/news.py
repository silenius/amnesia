# -*- coding: utf-8 -*-

from amnesia import db
from amnesia.models import content


class NewsQuery(content.ContentQuery):

    def __init__(self, *args, **kwargs):
        super(NewsQuery, self).__init__(*args, **kwargs)


class News(content.Content):

    query = db.Session.query_property(NewsQuery)

    FTS = [('title', 'A'), ('description', 'B'), ('body', 'C')]

    def __init__(self, **kwargs):
        super(News, self).__init__(**kwargs)
