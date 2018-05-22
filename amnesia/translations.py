# -*- coding: utf-8 -*-

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy import event
from sqlalchemy.types import String
from sqlalchemy.orm.collections import attribute_mapped_collection

from amnesia.modules.content import Content


def _localizer():
    return 'en'

def setup_translation(content_cls, translation_cls, localizer=None, **kwargs):
    '''Helper to setup translations'''

    if not localizer:
        localizer = _localizer

    content_mapper = orm.class_mapper(content_cls)
    translation_mapper = orm.class_mapper(translation_cls)

    content_mapper.add_properties({
        'current_translation': orm.relationship(
            lambda: translation_cls,
            primaryjoin=lambda: sql.and_(
                # XXX: use base_mapper.class_
                # pylint: disable=no-member
                orm.foreign(translation_cls.content_id) == Content.id,
                translation_cls.language_id == sql.bindparam(
                    None,
                    callable_=lambda: localizer(),
                    type_=String()
                )
            ),
            lazy='joined',
            uselist=False,
            innerjoin=True,
            viewonly=True,
            bake_queries=False,
            back_populates='content'
        ),

        'translations': orm.relationship(
            lambda: translation_cls,
            cascade='all, delete-orphan',
            #lazy='subquery',
            innerjoin=True,
            back_populates='content',
            collection_class=attribute_mapped_collection('language_id')
        )
    })

    translation_mapper.add_properties({
        'content': orm.relationship(
            lambda: content_cls,
            back_populates='translations',
            innerjoin=True,
            uselist=False
        ),
    })

def add_translation(config, content_cls, translation_cls,
                    localizer=_localizer):
    def register():
        trans = config.registry.setdefault('amnesia.translations', {})
        trans[content_cls] = translation_cls
    config.action(content_cls, register)


def includeme(config):
    config.add_directive('add_translation', add_translation)
