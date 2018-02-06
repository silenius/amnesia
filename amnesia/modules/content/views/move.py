# -*- coding: utf-8 -*-

# pylint: disable=E1101

from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow.fields import Integer
from marshmallow.validate import Range

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

from amnesia.modules.content import Entity


def includeme(config):
    ''' Pyramid includeme '''
    config.scan(__name__)


class WeightSchema(Schema):
    weight = Integer(required=True, validate=Range(min=1))


@view_config(name='weight', context=Entity, request_method='POST',
             renderer='json')
def weight(context, request):
    """Change the weight of a Content (within its container)
       Returns the number of updated Content (rows)."""

    try:
        result = WeightSchema().load(request.POST.mixed())
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)

    updated = context.change_weight(result['weight'])

    return {'updated': updated}
