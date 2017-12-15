# -*- coding: utf-8 -*-

from amnesia.modules.content import Content
from amnesia.modules.content_type import ContentType
from amnesia.modules.event import Event
from amnesia.modules.account import Account
#from amnesia.modules.country import Country
from amnesia.order import EntityOrder
from amnesia.order import Path


def includeme(config):

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.account.mapper')
    config.include('amnesia.modules.event.mapper')

    config.registry.settings['amnesia:orders'] = {
        'title': EntityOrder(Content, 'title', 'asc', doc='title'),
        'weight': EntityOrder(Content, 'weight', 'desc', doc='default'),
        'update': EntityOrder(
            Content, 'last_update', 'desc', doc='last update'
        ),
        'added': EntityOrder(Content, 'added', 'desc', doc='added date'),
        'type': EntityOrder(
            ContentType, 'name', 'asc', path=[Path(Content, 'type')],
            doc='content type'
        ),
        'owner': EntityOrder(Account, 'login', 'asc', path=[Path(Content,
                                                                    'owner')],
                              doc='owner'),
        'starts': EntityOrder(Event, 'starts', 'desc', doc='event starts'),
        'ends': EntityOrder(Event, 'ends', 'desc', doc='event ends'),

    #   'country' : EntityOrder(Country, 'name', 'asc', path=[Path(Event,
    #                                                               'country')],
    #                            doc='event country'),
#        'major' : EntityOrder(MimeMajor, 'name', 'asc',
#                              path=[Path(File, 'mime'), Path(Mime, 'major')],
#                              doc='mime')
    }
