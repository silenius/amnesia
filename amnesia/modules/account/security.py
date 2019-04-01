# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


def get_principals(userid, request):
    if userid and hasattr(request, 'user') and request.user:
        for role in request.user.roles:
            yield 'role:{}'.format(role.role.name)
            for permission in role.role.permissions:
                yield 'perm:{}'.format(permission.permission.name)
    return None
