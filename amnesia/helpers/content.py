# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.content import Content


#def dump_obj(obj, format, **kwargs):
#    return getattr(Serializer(obj), format)(**kwargs)


def polymorphic_hierarchy(cls=Content):
    return list(orm.class_mapper(cls).base_mapper.polymorphic_iterator())

