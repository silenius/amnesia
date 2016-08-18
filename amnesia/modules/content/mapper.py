# -*- coding: utf-8 -*-

from datetime import datetime

from pyramid.threadlocal import get_current_registry

from pytz import timezone

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy import event

from .model import Content
from ..account import Account
from ..state import State
from ..content_type import ContentType
from ..tag import Tag
from ..folder import Folder


@event.listens_for(Content, 'before_update', propagate=True)
def updated_listener(mapper, connection, target, **kwargs):
    registry = get_current_registry()
    tz = registry.settings.get('timezone', 'UTC')
    target.updated=datetime.now(timezone(tz))


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.account.mapper')
    config.include('amnesia.modules.state.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.tag.mapper')

    orm.mapper(Content, tables['content'],
        polymorphic_on=tables['content'].c.content_type_id,
        properties={

            # no need to load this column by default
            'fts': orm.deferred(tables['content'].c.fts),

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
                secondary=tables['content_tag']
            ),

            'parent': orm.relationship(
                Folder,
                foreign_keys=tables['content'].c.container_id,
                innerjoin=True,
                uselist=False,
                backref=orm.backref('children', cascade='all, delete-orphan')
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
            )

        })


