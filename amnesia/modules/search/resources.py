from collections import namedtuple
from datetime import date

from pyramid.authorization import Allow
from pyramid.authorization import Everyone

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.types import Date

from amnesia.resources import Resource
from amnesia.utils import polymorphic_ids
from amnesia.modules.content import Content

try:
    from amnesia_multilingual.utils import with_current_translations
    WITH_TRANSLATION=True
except ImportError:
    WITH_TRANSLATION=False

search_result = namedtuple(
    'SearchResult', ['result', 'count']
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

        stmt = sql.select(search_for)

        if 'amnesia.translations' in self.registry:
            stmt, lang_partition = with_current_translations(stmt, search_for)
            src = lang_partition.c
        else:
            src = search_for

        # Transform query to a ts_query
        q_ts = sql.func.plainto_tsquery(query)

        # Default string to highlight results (for ts_headline)
        hl_sel = "StartSel='<span class=\"search_hl\">', StopSel=</span>"

        # Highlight title and descriptions columns (through the ts_headline()
        # function)
        hl_title = sql.func.ts_headline(src.title, q_ts, hl_sel)
        hl_descr = sql.func.ts_headline(src.description, q_ts, hl_sel)

        # Where clause
        filters = [
            search_for.filter_published(),
            q_ts.op('@@')(src.fts),
            search_for.is_fts
        ]

        if types != '*':
            ids = polymorphic_ids(search_for, types)
            filters.append(search_for.content_type_id.in_(ids))

        filters = sql.and_(*filters)

        stmt = stmt.filter(filters)

        # Count how much rows we have
        count_stmt = sql.select(
            sql.func.count('*')
        ).select_from(
            stmt
        )

        count = self.dbsession.execute(count_stmt).scalar_one()

        # Add the two highlighted columns
        stmt = stmt.add_columns(
            hl_title.label('hl_title'),
            hl_descr.label('hl_descr')
        )

        stmt = stmt.order_by(
            q_ts.op('@@')(src.fts)
        )

        if limit:
            stmt = stmt.limit(limit)

        result = self.dbsession.execute(stmt)

        return search_result(result, count)

    def tag_id(self, tag, types='*', limit=None):
        ''' Search all Content which are linked to a specific tag '''
        # Base query
        search_for = orm.with_polymorphic(Content, types)
        stmt = sql.select(search_for)

        if 'amnesia.translations' in self.request.registry:
            stmt = stmt.join(
                search_for.current_translation
            ).options(
                orm.lazyload('*')
            )

        filters = [
            search_for.filter_published(),
            search_for.tags.any(id=tag.id)
        ]

        if types != '*':
            ids = polymorphic_ids(search_for, types)
            filters.append(search_for.content_type_id.in_(ids))

        filters = sql.and_(*filters)

        stmt = stmt.filter(filters)

        # Count how much rows we have
        count_stmt = sql.select(
            sql.func.count('*')
        ).select_from(
            stmt
        )

        count = self.dbsession.execute(count_stmt).scalar_one()

        if limit:
            stmt = stmt.limit(limit)

        result = self.dbsession.execute(stmt).scalars()

        return search_result(result, count)

    def search_added(self, year, month=None, day=None, types='*', limit=None):
        ''' Search by added date '''
        date_trunc = 'day' if day else 'month' if month else 'year'
        month, day = month or 1, day or 1

        search_date = date(year, month, day)
        search_for = orm.with_polymorphic(Content, types)
        search_query = sql.select(search_for)

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

        # Count how much rows we have
        count_stmt = sql.select(
            sql.func.count('*')
        ).select_from(
            stmt
        )

        count = self.dbsession.execute(count_stmt).scalar_one()

        search_query = search_query.order_by(search_for.added.desc())

        if limit:
            search_query = search_query.limit(limit)

        return search_result(search_query, count)
