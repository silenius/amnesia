# -*- coding: utf-8 -*-

import json
import logging

from operator import attrgetter

from sqlalchemy import inspect
from sqlalchemy import orm
from sqlalchemy import sql

from .modules.content import Content

log = logging.getLogger(__name__)

class Path:

    def __init__(self, class_, prop):
        self.class_ = class_
        self.prop = prop

    @property
    def class_(self):
        return self.mapper.entity

    @class_.setter
    def class_(self, value):
        self.mapper = orm.class_mapper(value)

    def __eq__(self, other):
        return self.class_ == other.class_ and self.prop == other.prop

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '%s.%s' % (self.class_.__name__, self.prop)

    def to_dict(self):
        return {
            'identity': self.mapper.polymorphic_identity,
            'prop': self.prop
        }


class EntityOrder:

    def __init__(self, src, prop, direction='asc', nulls=None, doc=None,
                 path=None):
        insp = inspect(src)
        self.src = src
        self._mapper = insp.mapper
        self.prop = prop
        self.direction = direction
        self.nulls = nulls
        self.doc = doc

        # If a path is required, the first one should be a polymorphic entity
        self.path = path if path is not None else []

    #######################################################################
    # PROPERTIES ##########################################################
    #######################################################################

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = 'desc' if value.lower() == 'desc' else 'asc'

    @property
    def nulls(self):
        return self._nulls

    @nulls.setter
    def nulls(self, value):
        try:
            value = value.lower()

            if value in ('first', 'last'):
                self._nulls = value
            else:
                self._nulls = None
        except:
            self._nulls = None

    @property
    def doc(self):
        if self._doc:
            return self._doc

        doc = [self.prop.replace('_', ' ')]
        return ' '.join(doc)

    @doc.setter
    def doc(self, value):
        try:
            value = value.strip()

            if value:
                self._doc = value
            else:
                raise ValueError
        except:
            self._doc = None

    #########################################################################

    def __eq__(self, other):
        if self.class_ == other.class_ and self.prop == other.prop:
            if self.path:
                if self.path == other.path:
                    return True
                return False
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def mapper(self):
        return self._mapper

    @property
    def class_(self):
        return self.mapper.class_

    @property
    def col(self):
        return getattr(self.class_, self.prop)

    @property
    def identity(self):
        return self.mapper.polymorphic_identity

    def to_dict(self):
        return {
            'identity': self.mapper.polymorphic_identity,
            'cls': self.mapper.entity.__name__,
            'prop': self.prop,
            'direction': self.direction,
            'nulls': self.nulls,
            'doc': self.doc,
            'path': [p.to_dict() for p in self.path]
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    JSON = to_json

    def to_sql(self, entity, direction=None, nulls=None):
        """ Returns an SQL expression """

        col = getattr(self.src, self.prop)

        if not direction:
            direction = self.direction

        if not nulls:
            nulls = self.nulls

        if direction == 'desc':
            col = col.desc()

        return col.nullslast() if nulls == 'last' else col.nullsfirst()

    @classmethod
    def from_dict(cls, data, pm):
        path = []

        for p in data['path']:
            mapper = pm.get(p['identity'])

            if mapper:
                mapper = mapper.class_

            path.append(Path(mapper, p['prop']))

        mapper = pm.get(data['identity'])
        if mapper:
            mapper = mapper.class_

        return cls(
            src=mapper,
            prop=data['prop'],
            direction=data['direction'],
            nulls=data['nulls'],
            doc='FIXME',
            path=path
        )

    def has_path(self, cls):
        for path in self.path:
            if path.class_ == cls or path.class_ is None:
                return True
        return False

    def polymorphic_entity(self, base):
        # The sort is on a polymorphic entity which is used in an
        # inheritance scenario and which share a common ancestor with
        # pl_cfg.base class (Content).
        # ex: Event.starts, File.file_size, ...
        if self.mapper.polymorphic_identity and self.mapper.isa(base):
            return self.mapper.entity

        # The sort is on a mapped class which is reachable # through a
        # polymorphic entity.
        # ex: Country.name (Content -> Event -> Country)
        if (self.path and self.path[0].mapper.polymorphic_identity and
                self.path[0].mapper.isa(base)):
            return self.path[0].mapper.entity

        return None


def for_entity(entity, orders):
    insp = inspect(entity)

    # insp is an AliasedInsp instance
    # entity is an AliasedClass.
    # ex: entity = orm.with_polymorphic(Content, [Page, Event])
    # insp.mapper -> <Mapper at 0x805aeb310; Content>
    if insp.is_aliased_class:
        if insp.with_polymorphic_mappers:
            cls = map(attrgetter('class_'), insp.with_polymorphic_mappers)
            cls = tuple(cls)
        else:
            cls = (insp.mapper.class_, )

        return {
            k: v for (k, v) in orders.items()
            if v.class_ in cls
            or any((v.has_path(c) for c in cls))
            or v.class_ is None
        }

    # Entity is an object instance
    # entity = Session.query(Page).get(id)
    elif isinstance(insp, orm.state.InstanceState):
        cls = list(map(attrgetter('class_'), insp.mapper.iterate_to_root()))
        base = insp.mapper.class_

        return {
            k: v for (k, v) in orders.items()
            if v.class_ in cls or v.has_path(base)
        }

    # Entity is a mapper (mapped class)
    elif isinstance(insp, orm.Mapper):
        cls = list(map(attrgetter('class_'), insp.iterate_to_root()))
        base = insp.base_mapper

        return {
            k: v for (k, v) in orders.items()
            if v.class_ in cls or v.has_path(base)
        }
