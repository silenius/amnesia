from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.modules.content import Content

from .model import Account
from .model import Role
from .model import AccountRole
from .model import Permission
from .model import RolePermission


def includeme(config):
    tables = config.registry['metadata'].tables

    # ACCOUNTS

    orm.mapper(Account, tables['account'], properties={
        'count_content': orm.column_property(
            sql.select(
                [sql.func.count()],
                tables['account'].c.id == tables['content'].c.owner_id
            ).label('count_content'),
            deferred=True
        ),

        'roles': orm.relationship(
            AccountRole, back_populates="account"
        )
    })

    # ROLES

    orm.mapper(Role, tables['role'], properties={
        'accounts': orm.relationship(
            AccountRole, back_populates="role"
        ),

        'permissions': orm.relationship(
            RolePermission, back_populates="role"
        )
    })

    orm.mapper(AccountRole, tables['account_role'], properties={
        'role': orm.relationship(
            Role, back_populates='accounts'
        ),

        'account': orm.relationship(
            Account, back_populates='roles'
        ),
    })

    # PERMISSIONS

    orm.mapper(Permission, tables['permission'], properties={
        'roles': orm.relationship(
            RolePermission, back_populates='permission'
        )
    })

    orm.mapper(RolePermission, tables['role_permission'], properties={
        'role': orm.relationship(
            Role, back_populates='permissions'
        ),

        'permission': orm.relationship(
            Permission, back_populates='roles'
        ),

        'content': orm.relationship(
            Content, back_populates='permissions'
        )
    })


@event.listens_for(orm.mapper, 'before_configured', once=True)
def _content_callback():
    orm.class_mapper(Content).add_property('permissions', orm.relationship(
        RolePermission, back_populates='content',
        order_by=RolePermission.weight
    ))
