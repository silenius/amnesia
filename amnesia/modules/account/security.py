# -*- coding: utf-8 -*-
# pylint: disable=no-member,singleton-comparison

import logging

from sqlalchemy import sql

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


def get_global_acls(request):
    user = request.user
    dbsession = request.dbsession
    principals = request.effective_principals

    acl_query = dbsession.query(GlobalACL)

    # Virtual roles which are in principals
    virtual = sql.and_(
        Role.virtual == True,
        Role.name.in_(principals)
    )

    # Select ACL for those virtual roles
    acl = acl_query.join(GlobalACL.role).filter(virtual)

    if user:
        user_roles = request.dbsession.query(AccountRole.role_id).filter_by(
            account_id=user.id)

        acl = acl.union(
            acl_query.filter(ContentACL.role_id.in_(user_roles))
        )

    return acl.order_by(GlobalACL.weight.desc()).all()

def get_entity_acls(request, entity):
    user = request.user
    dbsession = request.dbsession
    principals = request.effective_principals

    # ACL for specific entity ("local" ACL)
    acl_query = dbsession.query(ContentACL).filter_by(content=entity)

    # Virtual roles which are in principals
    virtual = sql.and_(
        Role.virtual == True,
        Role.name.in_(principals)
    )

    # Select ACL for those virtual roles
    acl = acl_query.join(ContentACL.role).filter(virtual)

    if user:
        # Roles for user
        user_roles = request.dbsession.query(AccountRole.role_id).filter_by(
            account_id=user.id)

        # If user, then add user's roles local ACL too
        acl = acl.union(
            acl_query.filter(ContentACL.role_id.in_(user_roles))
        )

    return acl.order_by(ContentACL.weight.desc()).all()
