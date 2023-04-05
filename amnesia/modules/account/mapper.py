from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.ext.associationproxy import association_proxy

from amnesia.db import mapper_registry
from amnesia.modules.content import Content

from .model import Account
from .model import AccountAuditLogin
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

    mapper_registry.map_imperatively(
        Account,
        tables['account'],
        properties={
            'count_content': orm.column_property(
                sql.select(
                    sql.func.count()
                ).where(
                    tables['account'].c.id == tables['content'].c.owner_id
                ).label(
                    'count_content'
                ),
                deferred=True
            ),

            'account_roles': orm.relationship(
                AccountRole,
                back_populates="account",
                cascade='all, delete-orphan'
            ),

            'audit_logins': orm.relationship(
                AccountAuditLogin,
                back_populates='account',
                cascade='all, delete-orphan'
            ),

        }
    )


    # ACCOUNT AUDIT LOGINS

    mapper_registry.map_imperatively(
        AccountAuditLogin,
        tables['account_audit_login'],
        properties={
            'account': orm.relationship(
                Account,
                back_populates='audit_logins'
            )
        }
    )

    # ROLES

    mapper_registry.map_imperatively(
        Role,
        tables['role'],
        properties={
            'accounts': orm.relationship(
                AccountRole,
                back_populates="role",
                cascade='all, delete-orphan'
            ),

            'acls': orm.relationship(
                ACL,
                back_populates="role",
                cascade='all, delete-orphan'
            ),

            'virtual': orm.column_property(
                sql.func.starts_with(
                    tables['role'].c.name, 'system.'
                )
            )
        }
    )

    mapper_registry.map_imperatively(
        AccountRole,
        tables['account_role'],
        properties={
            'role': orm.relationship(
                Role, back_populates='accounts'
            ),

            'account': orm.relationship(
                Account, back_populates='account_roles'
            ),
        }
    )

    # ACL RESOURCES

    mapper_registry.map_imperatively(
        ACLResource,
        tables['resource'],
        properties={
            'acls': orm.relationship(
                ACL, back_populates='resource'
            )
        }
    )

    # PERMISSIONS

    mapper_registry.map_imperatively(
        Permission,
        tables['permission'],
        properties={
            'acls': orm.relationship(
                ACL, back_populates='permission'
            )
        }
    )

    # ACCESS CONTROL LIST
    # TODO: include_properties/exclude_properties

    mapper_registry.map_imperatively(
        ACL, tables['acl'],
        polymorphic_on=tables['acl'].c.resource_id,
        properties={
            'role': orm.relationship(
                Role, back_populates='acls',
                innerjoin=True, lazy='joined'
            ),

            'permission': orm.relationship(
                Permission, back_populates='acls',
                innerjoin=True, lazy='joined'
            ),

            'resource': orm.relationship(
                ACLResource, back_populates='acls',
                innerjoin=True, lazy='joined'
            )
        })

    mapper_registry.map_imperatively(
        GlobalACL, inherits=ACL, polymorphic_identity=1,
    )

    mapper_registry.map_imperatively(
        ContentACL, inherits=ACL, polymorphic_identity=2,
        properties={
            'content': orm.relationship(
                Content, back_populates='acls'
            )
        }
    )


@event.listens_for(orm.mapper, 'before_configured', once=True)
def _content_callback():
    orm.class_mapper(Content).add_properties({
        'acls': orm.relationship(
            ContentACL,
            order_by=ContentACL.weight.desc(),
            back_populates='content',
            cascade='all, delete-orphan',
            lazy='subquery'
        ),
    })


@event.listens_for(Account, 'mapper_configured')
def _account_callback(mapper, class_):
    setattr(class_, 'roles', association_proxy('account_roles', 'role'))


@event.listens_for(Role, 'mapper_configured')
def _role_callback(mapper, class_):
    setattr(class_, 'permissions', association_proxy('acls', 'permission'))
