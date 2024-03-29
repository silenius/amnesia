import logging

from datetime import datetime

from pyramid.events import subscriber
from pyramid.threadlocal import get_current_registry

from pytz import timezone

import sqlalchemy.event
from sqlalchemy import sql
from sqlalchemy import orm

from amnesia.events import ObjectUpdateEvent
from amnesia.modules.content import Content
from amnesia.modules.account import Account
from amnesia.modules.state import State
from amnesia.modules.content_type import ContentType
from amnesia.modules.tag import Tag
from amnesia.modules.folder import Folder
from amnesia.db import mapper_registry

log = logging.getLogger(__name__)


@subscriber(ObjectUpdateEvent)
def updated_listener(event):
    obj = event.obj

    if isinstance(obj, Content):
        registry = get_current_registry()

        if registry and registry.settings:
            tz = registry.settings.get('timezone', 'UTC')
        else:
            tz = 'UTC'

        obj.updated = datetime.now(timezone(tz))


PGSQL_FTS_WEIGHTS = frozenset(('a', 'b', 'c', 'd'))
PGSQL_FTS_DEFAULT_WEIGHT = 'd'


@sqlalchemy.event.listens_for(Content, 'before_update', propagate=True)
@sqlalchemy.event.listens_for(Content, 'before_insert', propagate=True)
def update_fts_listener(mapper, connection, target):
    """ Set the 'fts' column (full text search) """

    fts = None

    if target.is_fts:
        # Check which columns should be indexed
        for i in getattr(target.__class__, '_FTS_', ()):
            (field, weight) = i

            if weight.lower() not in PGSQL_FTS_WEIGHTS:
                weight = PGSQL_FTS_DEFAULT_WEIGHT

            _fts = sql.func.coalesce(getattr(target, field, ''), '')
            _fts = sql.func.to_tsvector(_fts)
            _fts = sql.func.setweight(_fts, weight)

            fts = _fts if fts is None else fts.op('||')(_fts)

    target.fts = fts


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.account.mapper')
    config.include('amnesia.modules.state.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.tag.mapper')
    config.include('amnesia.modules.language.mapper')
    config.scan(__name__, categories=('pyramid', 'amnesia'))

    _count_alias = tables['content'].alias('_count_children')

    mapper_registry.map_imperatively(
        Content, tables['content'],
        polymorphic_on=tables['content'].c.content_type_id,
        properties={

            #################
            # RELATIONSHIPS #
            #################

            'owner': orm.relationship(
                Account,
                lazy='joined',
                innerjoin=True,
                backref=orm.backref('contents', lazy='dynamic',
                                    cascade='all, delete-orphan')
            ),

            'state': orm.relationship(
                State,
                lazy='joined',
                innerjoin=True
            ),

            'type': orm.relationship(
                ContentType,
                lazy='joined',
                innerjoin=True
            ),

            'tags': orm.relationship(
                Tag,
                secondary=tables['content_tag'],
                back_populates='contents'
            ),

            'parent': orm.relationship(
                lambda: Folder,
                foreign_keys=tables['content'].c.container_id,
                innerjoin=True,
                uselist=False,
                backref=orm.backref('children', cascade='all, delete-orphan')
            ),

            #####################
            # COLUMN PROPERTIES #
            #####################

            'position_in_container': orm.column_property(
                sql.func.row_number().over(
                    partition_by=tables['content'].c.container_id,
                    order_by=tables['content'].c.weight.desc()
                ),
                deferred=True,
                group='window_func'
            ),

            'count_children': orm.column_property(
                sql.select(
                    sql.func.count('*')
                ).where(
                    _count_alias.c.container_id == tables['content'].c.id
                ).correlate_except(
                    _count_alias
                ).scalar_subquery(),
                deferred=True
            )

        })
