# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPServerError
from pyramid.view import view_config

from sqlalchemy import orm

from amnesia import order
from amnesia.modules.content import Content
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder import FolderResource
from amnesia.modules.folder.validation import PolymorphicOrderSelectionSchema


def includeme(config):
    config.scan(__name__)


def polymorphic_orders(request):
    schema = PolymorphicOrderSelectionSchema()
    result, errors = schema.load(request.GET.mixed())

    if errors:
        raise HTTPServerError(errors)

    # Selected entities
    entities = result['entities']
    if entities:
        entity = orm.with_polymorphic(Content, entities)
    else:
        entity = Content

    orders = request.registry.settings['amnesia:orders']
    available_orders = order.for_entity(entity, orders)
    selected_orders = result['selected']
    all_orders = []

    if selected_orders:
        for o in selected_orders:
            try:
                _order = available_orders.pop(o['key'])
            except KeyError:
                pass
            else:
                _order = _order.to_dict()
                _order.update(o)
                _order['checked'] = True
                all_orders.append(_order)

    for (k, o) in available_orders.items():
        _order = o.to_dict()
        _order['checked'] = False
        _order['key'] = k
        all_orders.append(_order)

    return {
        'orders': all_orders
    }


# JSON

@view_config(name='polymorphic_orders', context=FolderEntity,
             request_method='GET', renderer='json', accept='application/json')
@view_config(name='polymorphic_orders', context=FolderResource,
             request_method='GET', renderer='json', accept='application/json')
def polymorphic_orders_json(context, request):
    return polymorphic_orders(request)

# HTML

@view_config(name='polymorphic_orders', context=FolderEntity,
             request_method='GET',
             renderer="amnesia:templates/content/_polymorphic_orders.pt")
@view_config(name='polymorphic_orders', context=FolderResource,
             request_method='GET',
             renderer="amnesia:templates/content/_polymorphic_orders.pt")
def polymorphic_orders_html(context, request):
    request.response.content_type = 'application/xml'
    return polymorphic_orders(request)
