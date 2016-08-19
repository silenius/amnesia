# -*- coding: utf-8 -*-

from operator import attrgetter

from sqlalchemy import orm
from sqlalchemy import sql

from .model import Folder
from amnesia import db


class FolderBrowser:

    def __call__(self, folder, sort_by=None, offset=0, limit=50, **kwargs):
        if sort_by is None:
            sort_by = ()

        #########
        # QUERY #
        #########

        # Polymorphic configuration of the folder
        pl_cfg = folder.polymorphic_config

        # Polymorphic entities that should be loaded. Order doesn't matter as
        # they will be loaded (LEFT JOIN) from the root entity (Content)
        with_polymorphic = pl_cfg.cls

        # For each sort, check if we need extra polymorphic entities to perform
        # the sort.
        for s in sort_by:
            entity = s.polymorphic_entity(pl_cfg.base_mapper)
            if entity:
                with_polymorphic.add(entity)

        entity = pl_cfg.base_mapper.entity
        if with_polymorphic:
            # Join entities if needed
            entity = orm.with_polymorphic(entity, with_polymorphic)

        q = dbsession.query(entity)

        for s in sort_by:
            contains_eager = None

            # The sort is on another mapped class which is reachable from the
            # base entity.
            # We have to JOIN some tables/entities, in other words we have to
            # find a "path".
            for path in s.path:
                #innerjoin = path.mapper.attrs[path.prop].innerjoin
                if path.mapper.attrs[path.prop].innerjoin:
                    join = q.join
                else:
                    join = q.outerjoin

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

        # Apply filters
        #q = q.filter(filters)

        # Count how much children we have in this container (used for
        # pagination)
        #count_filtered = q.count()

        ##########################
        # ORDER / LIMIT / OFFSET #
        ##########################

        sort_by = [o.to_sql() for o in sort_by]

    #        if params['sort_folder_first']:
    #            sort_by.insert(0, sql.func.lower(ContentType.name) != 'folder')

        # Query database
        # TODO: pagination based on OFFSET isn't scalable
        q = q.order_by(*sort_by).offset(offset).limit(limit)

        return q
