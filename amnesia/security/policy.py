import logging

from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper
from pyramid.authorization import Authenticated
from pyramid.authorization import Everyone
from pyramid.request import RequestLocalCache
from pyramid.settings import asbool

from sqlalchemy import sql


__all__ = ['cookie_security_policy']

log = logging.getLogger(__name__)


def cookie_security_policy(settings):
    cfg = {
        'http_only': asbool(settings.get('auth.http_only', 'true')),
        'secure': asbool(settings.get('auth.secure', 'false')),
        'secret': settings['auth.secret'],
    }

    helper = AmnesiaAuthTktCookieHelper(**cfg)

    return AmnesiaSecurityPolicy(helper)


class AmnesiaAuthTktCookieHelper(AuthTktCookieHelper):

    def userid(self, request):
        identity = self.identify(request)
        return None if identity is None else identity['userid']


class AmnesiaSecurityPolicy:

    def __init__(self, helper):
        self.helper = helper
        self.identity_cache = RequestLocalCache(self.load_user)
        self.acl = ACLHelper()

    def load_user(self, request):
        userid = self.helper.userid(request)

        if userid:
            from amnesia.modules.account import Account

            user = request.dbsession.execute(
                sql.select(Account).filter_by(id=userid, enabled=True)
            ).scalar_one_or_none()

            return user

        return None

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        """ Return a string ID for the user. """

        identity = self.identity(request)
        return None if identity is None else str(identity.id)

    def remember(self, request, userid, **kwargs):
        return self.helper.remember(request, userid, **kwargs)

    def forget(self, request, **kwargs):
        return self.helper.forget(request, **kwargs)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request, context)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request, context):
        principals = {Everyone}
        user = self.identity(request)

        if user is not None:
            principals.add(Authenticated)
            principals.add(f'u:{user.id}')

            for role in user.roles:
                if role.virtual:
                    principals.add(role.name)
                else:
                    principals.add(f'r:{role.name}')

        if hasattr(context, '__effective_principals__'):
            context_principals = context.__effective_principals__

            if callable(context_principals):
                context_principals = context_principals()

            if context_principals:
                principals.update(context_principals)

        return list(principals)
