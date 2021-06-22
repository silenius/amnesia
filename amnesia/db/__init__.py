# -*- coding: utf-8 -*-

from pyramid.settings import asbool
from pyramid.settings import aslist

from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker

# from .meta import metadata

import zope.sqlalchemy

from amnesia.utils.db import engine_from_config
from .meta import metadata
from .meta import mapper_registry


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    # The sessionmaker factory generates new Session objects when called.
    factory = sessionmaker(future=True)

    # An Engine with which newly created Session objects will be associated.
    factory.configure(bind=engine)

    return factory


def get_tm_session(session_factory, transaction_manager, request=None):
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
    dbsession = session_factory(info={"request": request})
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager
    )
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

    # hook to share the dbengine fixture in testing
    dbengine = settings.get('dbengine')
    if not dbengine:
        dbengine = get_engine(settings)

    session_factory = get_session_factory(dbengine)
    config.registry['dbsession_factory'] = session_factory

    config.registry['metadata'] = metadata
    config.registry['dbengine'] = dbengine

    if asbool(settings.get('amnesia.reflect_db', False)):
        metadata.reflect(bind=dbengine)

        schemas = aslist(settings.get('amnesia.reflect_schemas', []))
        for schema in schemas:
            metadata.reflect(bind=dbengine, schema=schema)

    # make request.dbsession available for use in Pyramid
    def dbsession(request):
        # hook to share the dbsession fixture in testing
        dbsession = request.environ.get('app.dbsession')
        if dbsession is None:
            # request.tm is the transaction manager used by pyramid_tm
            dbsession = get_tm_session(
                session_factory, request.tm, request=request
            )
        return dbsession

    config.add_request_method(dbsession, reify=True)
