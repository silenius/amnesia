# -*- coding: utf-8 -*-

# pylint: disable=E1101

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest

from marshmallow import Schema
from marshmallow import pre_load
from marshmallow.fields import List
from marshmallow.fields import Integer

from amnesia.utils.db import polymorphic_cls
from amnesia.utils.validation import as_list
from amnesia.modules.content import Content
from amnesia.modules.search import SearchResource


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class ArchiveSchema(Schema):
    ids = List(Integer(), missing=[])

    @pre_load
    def ensure_list(self, data, **kwargs):
        try:
            data['ids'] = as_list(data['ids'])
        except KeyError:
            data['ids'] = []

        return data


@view_config(context=SearchResource, name='archives', request_method='GET',
             renderer='amnesia:templates/search/archives.pt')
def archives(context, request):
    if len(request.subpath) > 3:
        raise HTTPNotFound()

    try:
        date_info = [int(_) for _ in request.subpath]
    except ValueError:
        raise HTTPNotFound()

    try:
        data = ArchiveSchema().load(request.GET.mixed())
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)

    if data['ids']:
        types = polymorphic_cls(Content, data['ids'])
    else:
        types = '*'

    search_query = context.search_added(
        *date_info, types=types, limit=500
    )

    return {
        'results': search_query.query.all(),
        'count': search_query.count,
        'date_info': date_info
    }

