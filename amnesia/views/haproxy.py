# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response


def includeme(config):
    config.scan(__name__)


@view_config(name='haproxy')
def haproxy(request):
    return Response(body='ok', content_type='text/plain')
