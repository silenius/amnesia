# -*- coding: utf-8 -*-

from sqlalchemy import inspect
from sqlalchemy import engine_from_config as _engine_from_config
from sqlalchemy.pool import NullPool


def polymorphic_ids(src, cls):
    """ Return polymorphic identities for the given mapped cls """

    return [
        k for k, v in inspect(src).mapper.base_mapper.polymorphic_map.items()
        if v.class_ in cls
    ]


def polymorphic_cls(src, ids):
    """ Return mapped classes for given polymorphic identities """

    return [
        v.class_ for k, v in
        inspect(src).mapper.base_mapper.polymorphic_map.items()
        if k in ids
    ]


def engine_from_config(configuration, *args, **kwargs):
    if configuration.get('sqlalchemy.poolclass') == 'NullPool':
        configuration['sqlalchemy.poolclass'] = NullPool

    return _engine_from_config(configuration, *args, **kwargs)
