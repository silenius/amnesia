# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from amnesia.modules.tag import Tag
from amnesia.modules.search import SearchResource


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(context=SearchResource, name='tag', request_method='GET',
             renderer='amnesia:templates/search/tag.pt')
def tag(context, request):
    tag_id = request.GET.get('id', '').strip()
    tag_obj = request.dbsession.get(Tag, tag_id)

    if not tag_obj:
        raise HTTPNotFound()

    search_query = context.tag_id(tag_obj, limit=500)

    return {
        'results': search_query.result,
        'count': search_query.count,
        'tag': tag_obj
    }

