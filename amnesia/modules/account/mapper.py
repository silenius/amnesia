from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.modules.content import Content

from .model import Account
from .model import Role
from .model import AccountRole
from .model import Permission
from .model import ACLResource
from .model import ACL
from .model import GlobalACL
from .model import ContentACL


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
            AccountRole, back_populates="role", cascade='all, delete-orphan'
        ),

        'acls': orm.relationship(
            ACL, back_populates="role", cascade='all, delete-orphan'
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

    # ACL RESOURCES

    orm.mapper(ACLResource, tables['resource'], properties={
        'acls': orm.relationship(
            ACL, back_populates='resource'
        )
    })

    # PERMISSIONS

    orm.mapper(Permission, tables['permission'], properties={
        'acls': orm.relationship(
            ACL, back_populates='permission'
        )
    })

    # ACCESS CONTROL LIST

    orm.mapper(
        ACL, tables['acl'],
        polymorphic_on=tables['acl'].c.resource_id,
        properties={
            'role': orm.relationship(
                Role, back_populates='acls'
            ),

            'permission': orm.relationship(
                Permission, back_populates='acls'
            ),

            'resource': orm.relationship(
                ACLResource, back_populates='acls'
            )
        })

    orm.mapper(
        GlobalACL, inherits=ACL, polymorphic_identity=1
    )

    orm.mapper(
        ContentACL, inherits=ACL,
        polymorphic_identity=2,
        properties={
            'content': orm.relationship(
                Content, back_populates='acls'
            )
        }
    )


@event.listens_for(orm.mapper, 'before_configured', once=True)
def _content_callback():
    orm.class_mapper(Content).add_property('acls', orm.relationship(
        ContentACL, back_populates='content'
    ))
