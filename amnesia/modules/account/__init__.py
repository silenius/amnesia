# -*- coding: utf-8 -*-

from pyramid.security import unauthenticated_userid

from .model import Account

from .resources import AuthResource
from .resources import DatabaseAuthResource


def _get_user(request):
    userid = unauthenticated_userid(request)

    if userid is not None:
        return request.dbsession.query(Account).filter_by(
            id=userid, enabled=True).first()

    return None


def includeme(config):
    config.add_request_method(_get_user, 'user', reify=True)

    config.include('.mapper')
    config.include('.views')
