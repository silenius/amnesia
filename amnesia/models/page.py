# -*- coding: utf-8 -*-

from amnesia import db
from amnesia.models import content


class PageQuery(content.ContentQuery):

    def __init__(self, *args, **kwargs):
        super(PageQuery, self).__init__(*args, **kwargs)


class Page(content.Content):

    query = db.Session.query_property(PageQuery)

    FTS = [('title', 'A'), ('description', 'B'), ('body', 'C')]

    def __init__(self, **kwargs):
        super(Page, self).__init__(**kwargs)
