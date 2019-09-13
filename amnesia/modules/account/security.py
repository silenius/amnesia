# -*- coding: utf-8 -*-

# pylint: disable=no-member,singleton-comparison

import logging

from pyramid.traversal import lineage

from sqlalchemy import sql
from sqlalchemy import orm

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

def get_entity_acl(request, entity, strict=False):
    dbsession = request.dbsession

    # ACL for specific entity ("local" ACL)
    acl_query = dbsession.query(ContentACL).filter_by(content=entity)

    if not strict:
        return acl_query.order_by(ContentACL.weight.desc()).all()

    user = request.user
    principals = request.effective_principals

    # Virtual roles which are in principals
    virtual = sql.and_(
        Role.virtual == True,
        Role.name.in_(principals)
    )

    # Select ACL for those virtual roles
    acl = acl_query.join(ContentACL.role).options(
        orm.contains_eager(ContentACL.role)).filter(virtual)

    if user:
        # Roles for user
        user_roles = dbsession.query(AccountRole.role_id).filter_by(
            account_id=user.id)

        # If user, then add user's roles local ACL too
        acl = acl.union(
            acl_query.filter(ContentACL.role_id.in_(user_roles))
        )

    return acl.order_by(ContentACL.weight.desc()).all()

def get_parent_acl(resource):
    parent_acl = []

    for res in lineage(resource):
        for ace in res.__acl__():
            parent_acl.append((res, ace))

    return parent_acl
