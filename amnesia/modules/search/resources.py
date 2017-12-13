# -*- coding: utf-8 -*-

# pylint: disable=E1101

from collections import namedtuple
from datetime import date

from pyramid.security import Allow
from pyramid.security import Everyone

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.types import Date

from amnesia.resources import Resource
from amnesia.utils import polymorphic_ids
from amnesia.modules.content import Content

search_result = namedtuple(
    'SearchResult', ['query', 'count']
)


class SearchResource(Resource):
    ''' Manage the site search '''

    __name__ = 'search'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    def __acl__(self):
        yield Allow, Everyone, 'search'
        yield from super().__acl__()

    def fulltext(self, query, types='*', limit=None):
        # Base query
        search_for = orm.with_polymorphic(Content, types)
        search_query = self.dbsession.query(search_for)

        # Transform query to a ts_query
        q_ts = sql.func.plainto_tsquery(query)

        # Default string to highlight results (for ts_headline)
        hl_sel = "StartSel='<span class=\"search_hl\">', StopSel=</span>"

        # Highlight title and descriptions columns (through the ts_headline()
        # function)
        hl_title = sql.func.ts_headline(Content.title, q_ts, hl_sel)
        hl_descr = sql.func.ts_headline(Content.description, q_ts, hl_sel)

        # Where clause
        filters = sql.and_(
            search_for.filter_published(),
            q_ts.op('@@')(Content.fts),
            Content.is_fts
        )

        if types != '*':
            ids = polymorphic_ids(search_for, types)
            filters.append(search_for.content_type_id.in_(ids))

        search_query = search_query.filter(filters)

        # Count how much rows we have
        count = search_query.count()

        # Add the two highlighted columns
        search_query = search_query.add_columns(
            hl_title.label('hl_title'),
            hl_descr.label('hl_descr')
        )

        search_query = search_query.order_by(
            q_ts.op('@@')(Content.fts)
        )

        if limit:
            search_query = search_query.limit(limit)

        return search_result(search_query, count)

    def tag_id(self, tag, types='*', limit=None):
        ''' Search all Content which are linked to a specific tag '''
        # Base query
        search_for = orm.with_polymorphic(Content, types)
        search_query = self.dbsession.query(search_for)

        filters = sql.and_(
            search_for.filter_published(),
            search_for.tags.any(id=tag.id)
        )

        if types != '*':
            ids = polymorphic_ids(search_for, types)
            filters.append(search_for.content_type_id.in_(ids))

        search_query = search_query.filter(filters)
        count = search_query.count()

        if limit:
            search_query = search_query.limit(limit)

        return search_result(search_query, count)

    def search_added(self, year, month=None, day=None, types='*', limit=None):
        ''' Search by added date '''
        date_trunc = 'day' if day else 'month' if month else 'year'
        month, day = month or 1, day or 1

        search_date = date(year, month, day)
        search_for = orm.with_polymorphic(Content, types)
        search_query = self.dbsession.query(search_for)

        filters = sql.and_(
            search_for.filter_published(),
            sql.func.date_trunc(
                date_trunc,
                sql.cast(search_for.added, Date)
            ) == sql.func.date_trunc(
                date_trunc, search_date
            )
        )

        if types != '*':
            ids = polymorphic_ids(search_for, types)
            filters.append(search_for.content_type_id.in_(ids))

        search_query = search_query.filter(filters)
        count = search_query.count()

        search_query = search_query.order_by(search_for.added.desc())

        if limit:
            search_query = search_query.limit(limit)

        return search_result(search_query, count)
