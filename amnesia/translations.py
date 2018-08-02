# -*- coding: utf-8 -*-

import logging

from pyramid.threadlocal import get_current_registry

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy import event
from sqlalchemy.types import String
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property

from amnesia.modules.content import Content

log = logging.getLogger(__name__)


def _localizer():
    return 'en'

#from types import MappingProxyType
#default_config = {'a': 1}
#DEFAULTS = MappingProxyType(default_config)

def setup_translation(content_cls, translation_cls, localizer=None, **kwargs):
    '''Helper to setup translations'''

    log.debug('Adding translation properties: %s to %s', content_cls,
              translation_cls)

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


def make_hybrid(name):

    @hybrid_property
    def _column(self):
        return getattr(self.current_translation, name)

    @_column.setter
    def _column(self, value):
        setattr(self.current_translation, name, value)

    #@_column.expression
    #def _column(cls):
    #    return cls.current_translation.has()

    _column.__name__ = name

    return _column


_TRANSLATIONS_KEY = 'amnesia.translations'


def _setup_translation():
    log.info('SQLAlchemy after_configured handler _setup_translation called')
    registry = get_current_registry()

    if _TRANSLATIONS_KEY not in registry:
        return

    _cfg = registry[_TRANSLATIONS_KEY]

    if 'mappings' in _cfg:
        for cls, tr_cls in _cfg['mappings'].items():
            setup_translation(cls, tr_cls)

    if 'attrs' in _cfg:
        for cls, cols in _cfg['attrs'].items():
            for col in cols:
                log.debug('Adding hybrid attribute: %s.%s', cls, col)
                setattr(cls, col, make_hybrid(col))


def set_translatable_attrs(config, cls, cols):
    _attrs = config.registry.\
        setdefault(_TRANSLATIONS_KEY, {}).\
        setdefault('attrs', {})

    _attrs[cls] = cols


def set_translatable_mapping(config, cls, trans_cls):
    _mappings = config.registry.\
        setdefault(_TRANSLATIONS_KEY, {}).\
        setdefault('mappings', {})

    _mappings[cls] = trans_cls


def includeme(config):
    event.listen(orm.mapper, 'after_configured', _setup_translation)
    config.add_directive('set_translatable_attrs', set_translatable_attrs)
    config.add_directive('set_translatable_mapping', set_translatable_mapping)
    config.add_translation_dirs('amnesia:locale/')
