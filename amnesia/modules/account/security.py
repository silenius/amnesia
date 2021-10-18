# pylint: disable=no-member,singleton-comparison

import logging

from pyramid.authorization import Everyone
from pyramid.authorization import Authenticated
from pyramid.traversal import lineage

from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy.types import Integer

from amnesia.modules.content import Content
from amnesia.modules.account import ACL
from amnesia.modules.account import ContentACL
from amnesia.modules.account import GlobalACL
from amnesia.modules.account import AccountRole
from amnesia.modules.account import Role

log = logging.getLogger(__name__)


def get_principals(userid, request):
    if userid and hasattr(request, 'user') and request.user:
        for role in request.user.roles:
            yield f'r:{role.role.name}'

    return None

def get_global_acl(dbsession, identity=None):
    stmt = sql.select(
        GlobalACL
    ).join(
        GlobalACL.role
    ).options(
        orm.contains_eager(GlobalACL.role)
    )

    if identity:
        filters = sql.or_(
            Role.accounts.any(account_id=identity.id),
            GlobalACL.role.has(Role.name.in_([Authenticated, Everyone])),
         )
    else:
        filters = GlobalACL.role.has(name=Everyone)

    stmt = stmt.filter(filters).order_by(GlobalACL.weight.desc())

    return dbsession.execute(stmt).scalars().all()

def get_content_acl(dbsession, entity, recursive=False, with_global_acl=True):
    # We want ACL for this entity only
    if not recursive:
        # Content ACL only
        if not with_global_acl:
            result = dbsession.execute(
                sql.select(
                    ContentACL
                ).filter_by(
                    content=entity
                ).order_by(
                    ContentACL.weight.desc()
                )
            ).scalars().all()

            return result

        # Content ACL and Global ACL
        acl_types = orm.with_polymorphic(
            ACL, [ContentACL, GlobalACL]
        )

        # Select Content ACL for this entity or Global ACL
        filters = sql.or_(
            acl_types.ContentACL.content == entity,
            ACL.resource.of_type(GlobalACL)
        )

        stmt = sql.select(
            acl_types
        ).join(
            acl_types.resource
        ).options(
            orm.contains_eager(acl_types.resource)
        ).filter(
            filters
        ).order_by(
            sql.desc(ACL.resource.of_type(ContentACL)),
            acl_types.ContentACL.weight.desc(),
            sql.desc(ACL.resource.of_type(GlobalACL)),
            acl_types.GlobalACL.weight.desc()
        )

        return dbsession.execute(stmt).scalars().all()

    # Recursive ACL, we need to fetch hierarchy first
    contents = sql.select(
        Content, sql.literal(1, type_=Integer).label('level')
    ).filter(
        Content.id == entity.id
    ).cte(
        name=f'content_acl_{entity.id}', recursive=True
    )

    contents_join = sql.select(
        Content, contents.c.level + 1
    ).join(
        contents, contents.c.container_id == Content.id
    )

    contents = contents.union_all(contents_join)

    content_acls = sql.select(
        ContentACL
    ).join(
        contents, contents.c.id == ContentACL.content_id
    )

    if with_global_acl:
        content_acls = content_acls.add_columns(
            contents.c.level.label('level')
        )

        global_acls = sql.select(
            GlobalACL, sql.literal(None).label('level')
        )

        acls = content_acls.union_all(
            global_acls
        ).subquery()

        au = orm.aliased(ACL, acls)

        stmt = sql.select(
            au
        ).order_by(
            acls.c.level.nullslast(),
            acls.c.weight.desc()
        )

        return dbsession.execute(stmt).scalars().all()

    stmt = content_acls.order_by(
        contents.c.level,
        contents.c.weight.desc()
    )

    return dbsession.execute(stmt).scalars().all()

def get_parent_acl(resource):
    parent_acl = []

    for res in lineage(resource):
        for ace in res.__acl__():
            parent_acl.append((res, ace))

    return parent_acl
