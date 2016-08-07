from sqlalchemy import orm
from sqlalchemy import sql

from .model import Account


def includeme(config):
    tables = config.registry['metadata'].tables

    orm.mapper(Account, tables['account'],
        properties={
            'count_content': orm.column_property(
                sql.select(
                    [sql.func.count()],
                    tables['account'].c.id == tables['content'].c.owner_id
                ).label('count_content'),
                deferred=True
            )
        })
