# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from collections import namedtuple
from operator import attrgetter

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.modules.content_type import ContentType

try:
    from amnesia_multilingual.utils import with_current_translations
    WITH_TRANSLATION=True
except ImportError:
    WITH_TRANSLATION=False

log = logging.getLogger(__name__)

FolderBrowserResult = namedtuple(
    'FolderBrowserResult',
    ['query', 'sort', 'count']
)

class FolderBrowser:

    def __init__(self, folder, dbsession):
        self.folder = folder
        self.dbsession = dbsession

    def query(self, sort_by=(), offset=0, limit=None, deferred=(),
              undeferred=(), sort_folder_first=False, count=True,
              filter_types=(), only_published=True, **kwargs):

        if limit is None:
            limit = self.folder.default_limit

        #########
        # QUERY #
        #########

        # Polymorphic configuration of the folder
        pl_cfg = self.folder.polymorphic_config

        # Polymorphic entities that should be loaded. Order doesn't matter as
        # they will be loaded (LEFT JOIN) from the root entity (Content)
        with_polymorphic = pl_cfg.cls

        # For each sort, check if we need extra polymorphic entities to perform
        # the sort.
        for s in sort_by:
            entity = s.polymorphic_entity(pl_cfg.base_mapper)
            if entity:
                with_polymorphic.append(entity)

        # A folder contains "entities" which all inherit from the same "root"
        # base class (Content), which will be our starting point to build the
        # query object
        entity = pl_cfg.base_mapper.entity

        if with_polymorphic:
            # Ensure that each descendant mapper's tables are included in the
            # FROM clause
            entity = orm.with_polymorphic(entity, with_polymorphic)

        # Ok, now we have our base entity \o/
        q = sql.select(entity)

        # If amnesia_multilingual is enabled then we must JOIN the translation
        # tables too
        if WITH_TRANSLATION:
            (q, lang_partition) = with_current_translations(q, entity)

        #########
        # SORTS #
        #########

        for s in sort_by:
            contains_eager = None

            # The sort is on another mapped class which is reachable from the
            # base entity.
            # We have to JOIN some tables/entities, in other words we have to
            # find a "path".
            for path in s.path:
                _is_innerjoin = path.mapper.attrs[path.prop].innerjoin
                join = q.join if _is_innerjoin else q.outerjoin

                # Case 1: the sort is on a mapped class which is directly
                # available from the base class through a property.
                # ex: ContentType.name (Content -> "type").
                if path.mapper.entity is pl_cfg.base_mapper.entity:
                    q = join(path.prop)
                    contains_eager = orm.contains_eager(path.prop)

                # Case 2: the sort is on a mapped class which is reachable
                # through a polymorphic entity
                # ex: Country.name (Content -> Event -> Country)
                elif (path.mapper.polymorphic_identity and
                      path.mapper.isa(pl_cfg.base_mapper)):

                    # If we order on Foo.bar we must get it from the
                    # polymorphic entity, ex: entity.Foo.bar
                    prop = '{0}.{1}'.format(path.class_.__name__, path.prop)

                    # Fetch the given prop from the entity
                    prop = attrgetter(prop)
                    q = join(prop(entity))

                    if not contains_eager:
                        contains_eager = orm.contains_eager(prop(entity))
                    else:
                        contains_eager = contains_eager.contains_eager(
                            prop(entity))

                # Case 3: the sort is on a mapped class, but extra steps are
                # needed (JOINs) to "reach" the sort.
                # ex: MimeMajor.name (Content -> File -> Mime -> MimeMajor)
                else:
                    prop = attrgetter(path.prop)
                    q = join(prop(path.class_))

                    contains_eager = contains_eager.contains_eager(
                        prop(path.class_))

            if contains_eager:
                q = q.options(contains_eager)

        ###########
        # FILTERS #
        ###########

        filters = entity.parent == self.folder

        if only_published:
            filters = sql.and_(
                filters,
                entity.filter_published()
            )

        if filter_types:
            q = q.join(entity.type).options(orm.contains_eager(entity.type))

            filters = sql.and_(
                sql.func.lower(ContentType.name).in_(filter_types),
                filters
            )

        # Apply filters
        q = q.filter(filters)

        # Count how much children we have in this container (used for
        # pagination)
        stmt_count = sql.select(
            sql.func.count('*')
        ).select_from(q)

        count = self.dbsession.execute(stmt_count).scalar_one()

        ##########################
        # ORDER / LIMIT / OFFSET #
        ##########################

#        if sort_by:
#            sort_by = [o.to_sql(entity) for o in sort_by]
#        else:
#            sort_by = [entity.weight.desc()]

        sort_by = []

        if sort_folder_first:
            q = q.join(entity.type).options(orm.contains_eager(entity.type))
            sort_by.insert(0, sql.func.lower(ContentType.name) != 'folder')

        # Query database
        # FIXME: OFFSET based pagination isn't scalable
        q = q.options(
            *(orm.defer(p) for p in deferred),
            *(orm.undefer(p) for p in undeferred)
        ).order_by(*sort_by).offset(offset).limit(limit)

        result = self.dbsession.execute(q).scalars()

        return FolderBrowserResult(result, sort_by, count)
