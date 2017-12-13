# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy import sql

from pyramid.view import view_config

from amnesia.modules.document import Document
from amnesia.modules.document import DocumentResource


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(request_method='GET', context=DocumentResource, name='newshome',
             renderer='amnesia:templates/document/view/_news_home.pt')
def newshome(context, request):
    news_container = request.registry.settings.get('news_container_id')

    if not news_container:
        documents = []
    else:
        filters = sql.and_(
            Document.filter_published(),
            Document.filter_container_id(news_container)
        )

        query = context.query()
        query = query.filter(filters).order_by(Document.added.desc()).limit(5)

        documents = query.all()

    return {
        'documents': documents,
        'news_container': news_container
    }
