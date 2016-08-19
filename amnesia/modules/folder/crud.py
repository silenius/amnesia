# -*- coding: utf-8 -*-

from pyramid.response import Response

import logging

log = logging.getLogger(__name__)


def create(request):
    pass


def read(resource, request):
    return Response('FOLDER READ')


def update(request):
    pass


def modify(request):
    pass


def delete(request):
    pass
