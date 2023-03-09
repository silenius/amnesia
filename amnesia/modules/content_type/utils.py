# -*- coding: utf-8 -*-

import transaction

from sqlalchemy import sql


def get_type_id(config, name):
    """ This function returns the content_type id for a given name """

    dbsession = config.registry['dbsession_factory']()
    tables = config.registry['metadata'].tables

    q = sql.select(
        tables['content_type'].c.id
    ).where(
        tables['content_type'].c.name == name
    )

    # FIXME: let the transaction manager handle that lifecycle
    content_type_id = dbsession.execute(q).scalar()
    dbsession.close()

    if not content_type_id:
        raise ValueError('No such type: {}'.format(name))

    return content_type_id
