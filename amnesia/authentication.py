# -*- coding: utf-8 -*-

import logging

from pyramid.authentication import AuthTktAuthenticationPolicy

log = logging.getLogger(__name__)

from pyramid.security import Authenticated
from pyramid.security import Everyone


class AmnesiaAuthenticationPolicy(AuthTktAuthenticationPolicy):

    def authenticated_userid(self, request):
        if hasattr(request, 'user') and request.user:
            return request.user.id

    def effective_principals(self, request):
        principals = [Everyone]

        if hasattr(request, 'user') and request.user:
            principals.append(Authenticated)
            principals.append(str(request.user.id))

            for role in request.user.roles:
                principals.append('role:{}'.format(role.role.name))

        return principals
