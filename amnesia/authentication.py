# -*- coding: utf-8 -*-

import logging

from pyramid.authentication import AuthTktAuthenticationPolicy

from pyramid.security import Authenticated
from pyramid.security import Everyone

log = logging.getLogger(__name__)

class AmnesiaAuthenticationPolicy(AuthTktAuthenticationPolicy):

    def authenticated_userid(self, request):
        if hasattr(request, 'user') and request.user:
            return request.user.id

    def effective_principals(self, request):
        principals = {Everyone}

        if hasattr(request, 'user') and request.user:
            principals.add(Authenticated)
            principals.add(str(request.user.id))

            for role in request.user.roles:
                if role.virtual:
                    principals.add(role.name)
                else:
                    principals.add('role:{}'.format(role.name))

        return principals
