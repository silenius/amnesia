# -*- coding: utf-8 -*-

# pylint: disable=no-member,singleton-comparison

import logging

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
            yield 'role:{}'.format(role.role.name)

    return None

# FIXME: add orm.contains_eager

def get_global_acl(request, strict=False):
    dbsession = request.dbsession

    acl_query = dbsession.query(GlobalACL)

    if not strict:
        return acl_query.order_by(GlobalACL.weight.desc()).all()

    user = request.user
    principals = request.effective_principals

    # Virtual roles which are in principals
    virtual = sql.and_(
        Role.virtual == True,
        Role.name.in_(principals)
    )

    # Select ACL for those virtual roles
    acl = acl_query.join(GlobalACL.role).options(
        orm.contains_eager(GlobalACL.role)).filter(virtual)

    if user:
        user_roles = dbsession.query(AccountRole.role_id).filter_by(
            account_id=user.id)

        acl = acl.union(
            acl_query.filter(ContentACL.role_id.in_(user_roles))
        )

    return acl.order_by(GlobalACL.weight.desc()).all()

def get_content_acl(request, entity, recursive=False, with_global_acl=True):
    dbsession = request.dbsession

    if not recursive:
        if not with_global_acl:
            return dbsession.query(ContentACL).filter_by(
                content=entity).order_by(ContentACL.weight.desc()).all()

        acl_types = orm.with_polymorphic(ACL, [ContentACL, GlobalACL])

        return dbsession.query(acl_types).join(acl_types.resource).options(
            orm.contains_eager(acl_types.resource)
        ).filter(
            sql.or_(acl_types.ContentACL.content == entity,
                    ACL.resource.of_type(GlobalACL))
        ).order_by(
            sql.desc(ACL.resource.of_type(ContentACL)),
            acl_types.ContentACL.weight.desc(),
            sql.desc(ACL.resource.of_type(GlobalACL)),
            acl_types.GlobalACL.weight.desc()
        ).all()

    # Recursive ACL, we need to fetch hierarchy first
    contents = dbsession.query(
        Content, sql.literal(1, type_=Integer).label('level')
    ).filter(Content.id == entity.id).cte(name='all_content', recursive=True)

    contents_join = dbsession.query(Content, contents.c.level + 1).join(
        contents, contents.c.container_id == Content.id
    )

    contents = contents.union_all(contents_join)

    content_acls = dbsession.query(ContentACL).join(
        contents, contents.c.id == ContentACL.content_id
    )

    if with_global_acl:
        content_acls = content_acls.add_columns(
            contents.c.level.label('level')
        )

        global_acls = dbsession.query(GlobalACL,
                                      sql.literal(None).label('level'))

        acls = content_acls.union_all(global_acls).subquery()

        return dbsession.query(ACL).select_entity_from(acls).order_by(
            acls.c.level.nullslast(), acls.c.acl_weight.desc()
        ).all()

    return content_acls.order_by(
        contents.c.level, contents.c.weight.desc()
    ).all()

def get_parent_acl(resource):
    parent_acl = []

    for res in lineage(resource):
        for ace in res.__acl__():
            parent_acl.append((res, ace))

    return parent_acl
