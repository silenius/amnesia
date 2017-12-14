# -*- coding: utf-8 -*-


from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import Everyone
from pyramid.security import Authenticated


def includeme(config):
    pass


class DbAuthenticationPolicy(AuthTktAuthenticationPolicy):

    def authenticated_userid(self, request):
        return request.user.id if request.user is not None else None

    def effective_principals(self, request):
        principals = [Everyone]
        userid = self.authenticated_userid(request)

        if userid:
            principals += [Authenticated, userid]

        return principals
