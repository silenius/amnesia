# -*- coding: utf-8 -*-

from datetime import datetime

from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import get_current_request

from pytz import timezone

from sqlalchemy import event
from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.types import String

from .model import Content
from .model import ContentTranslation
from amnesia.modules.account import Account
from ..state import State
from ..content_type import ContentType
from ..tag import Tag
from ..folder import Folder
from amnesia.modules.language import Language


@event.listens_for(Content, 'before_update', propagate=True)
def updated_listener(mapper, connection, target):
    registry = get_current_registry()
    tz = registry.settings.get('timezone', 'UTC')
    target.updated = datetime.now(timezone(tz))


PGSQL_FTS_WEIGHTS = frozenset(('a', 'b', 'c', 'd'))
PGSQL_FTS_DEFAULT_WEIGHT = 'd'


@event.listens_for(Content, 'before_update', propagate=True)
@event.listens_for(Content, 'before_insert', propagate=True)
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

    _count_alias = tables['content'].alias('_count_children')

    orm.mapper(
        ContentTranslation, tables['content_translation'],
        polymorphic_on=tables['content_translation'].c.content_type_id,
        properties={
            'language': orm.relationship(
                Language,
                lazy='joined',
                innerjoin=True,
                uselist=False
            ),

            'content': orm.relationship(
                Content,
                innerjoin=True,
                uselist=False,
                back_populates='translations'
            ),

            'type': orm.relationship(
                ContentType,
                lazy='joined',
                innerjoin=True,
                viewonly=True,
                uselist=False
            ),
        }
    )

    orm.mapper(
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
                Folder,
                foreign_keys=tables['content'].c.container_id,
                innerjoin=True,
                uselist=False,
                backref=orm.backref('children', cascade='all, delete-orphan')
            ),

            # pylint: disable=no-member
            'current_translation': orm.relationship(
                ContentTranslation,
                primaryjoin=lambda: sql.and_(
                    ContentTranslation.content_id == Content.id,
                    ContentTranslation.language_id == sql.bindparam(
                        None,
                        callable_=lambda: get_current_request().locale_name,
                        type_=String()
                    )
                ),
                lazy='joined',
                uselist=False,
                innerjoin=True,
                viewonly=True,
                bake_queries=False,
                #back_populates='content'
            ),

            'translations': orm.relationship(
                ContentTranslation,
                back_populates='content',
                cascade='all, delete-orphan',
                #lazy='subquery',
                innerjoin=True,
                collection_class=attribute_mapped_collection('language_id')
            ),

            #####################
            # COLUMN PROPERTIES #
            #####################

            'position_in_container': orm.column_property(
                sql.func.row_number().
                over(partition_by=tables['content'].c.container_id,
                     order_by=tables['content'].c.weight.desc()),
                deferred=True,
                group='window_func'
            ),

            # FIXME: move to folder mapper with a LATERAL expression
            'count_children': orm.column_property(
                sql.select([sql.func.count()]).where(
                    _count_alias.c.container_id == tables['content'].c.id
                ).correlate(tables['content']).label('count_children'),
                deferred=True
            ),

        })
