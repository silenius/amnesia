from sqlalchemy import orm
from sqlalchemy import sql

from .model import Account


def includeme(config):
    tables = config.registry['metadata'].tables

    orm.mapper(Account, tables['public.account'],
        properties={
            'count_content': orm.column_property(
                sql.select(
                    [sql.func.count()],
                    tables['public.account'].c.id == tables['public.content'].c.owner_id
                ).label('count_content'),
                deferred=True
            )
        })
