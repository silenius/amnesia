# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.view import view_config

from amnesia.modules.account import AuthResource


def includeme(config):
    config.scan(__name__)


@view_config(name='logout', context=AuthResource, permission='logout',
             request_method='GET')
def logout(context, request):
    headers = forget(request)
    request.session.invalidate()
    location = request.application_url
    return HTTPFound(location=location, headers=headers)
