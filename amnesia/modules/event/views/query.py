# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy import sql

from pyramid.view import view_config

from amnesia.modules.event import Event
from amnesia.modules.event import EventResource


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(request_method='GET', context=EventResource, name='sliderhome',
             renderer='amnesia:templates/event/view/_slider_home.pt')
def sliderhome(context, request):
    filters = sql.and_(
        Event.filter_published(),
        sql.not_(Event.filter_finished())
    )

    query = context.query()
    query = query.filter(filters).order_by(Event.starts).limit(10)

    return {'events': query.all()}
