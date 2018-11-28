# -*- coding: utf-8 -*-

from pyramid.settings import aslist

from sqlalchemy import engine_from_config
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# from .meta import metadata

import zope.sqlalchemy

def get_engine(settings, prefix='sqlalchemy.'):
    if settings.get('sqlalchemy.poolclass') == 'NullPool':
        settings['sqlalchemy.poolclass'] = NullPool
    return engine_from_config(settings, prefix)


def get_metadata(settings):
    return MetaData()


def get_session_factory(engine):
    # The sessionmaker factory generates new Session objects when called.
    factory = sessionmaker()

    # An Engine with which newly created Session objects will be associated.
    factory.configure(bind=engine)

    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(dbsession,
                             transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('amnesia.db')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')
    engine = get_engine(settings)
    meta = get_metadata(settings)

    # reflection
    for schema in aslist(settings.get('amnesia.reflect_schemas', [])):
        meta.reflect(bind=engine, schema=schema)

    session_factory = get_session_factory(engine)
    config.registry['dbsession_factory'] = session_factory
    config.registry['metadata'] = meta

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )
