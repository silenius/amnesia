# -*- coding: utf-8 -*-

# pylint: disable=E1101

import operator

import transaction

from marshmallow import Schema
from marshmallow.fields import Integer
from marshmallow.validate import Range

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from sqlalchemy import sql

from amnesia.modules.content import Content
from amnesia.modules.content import Entity


def includeme(config):
    config.scan(__name__)


class WeightSchema(Schema):
    weight = Integer(required=True, validate=Range(min=1))


@view_config(name='weight', context=Entity, request_method='POST',
             renderer='json')
def weight(context, request):
    """Change the weight of a Content (within its container)
       Returns the number of updated Content (rows)."""

    result, errors = WeightSchema().load(request.POST.mixed())

    if errors:
        raise HTTPInternalServerError()

    _weight = result['weight']

    obj = request.dbsession.query(Content).enable_eagerloads(False).\
        with_lockmode('update').get(context.entity.id)

    (min_weight, max_weight) = sorted((_weight, obj.weight))

    # Do we move downwards or upwards ?
    if _weight - obj.weight > 0:
        operation = operator.sub
        whens = {min_weight: max_weight}
    else:
        operation = operator.add
        whens = {max_weight: min_weight}

    # Select all the rows between the current weight and the new weight
    filters = sql.and_(
        Content.container_id == obj.container_id,
        Content.weight.between(min_weight, max_weight)
    )

    # Swap min_weight/max_weight, or increment/decrement by one depending on
    # whether one moves up or down
    new_weight = sql.case(
        value=Content.weight, whens=whens,
        else_=operation(Content.weight, 1)
    )

    try:
        # The UPDATE statement
        updated = request.dbsession.query(Content).enable_eagerloads(False).\
            filter(filters).update({'weight': new_weight},
                                   synchronize_session=False)
        transaction.commit()
        return {'updated': updated}
    except:
        raise HTTPInternalServerError()
