# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from amnesia.modules.search import SearchResource


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(context=SearchResource, name='', request_method='GET',
             renderer='amnesia:templates/search/general.pt')
def search(context, request):
    query = request.GET.get('query', '').strip()

    if not query:
        raise HTTPNotFound()

    search_query = context.fulltext(query, limit=500)

    return {
        'results': search_query.result,
        'count': search_query.count,
        'query': query
    }

