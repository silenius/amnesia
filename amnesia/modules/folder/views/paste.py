# -*- coding: utf-8 -*-

# pylint: disable=E1101

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.content.validation import IdListSchema
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder.exc import PasteError


def includeme(config):
    config.scan(__name__)


@view_config(request_method='POST', name='paste', context=FolderEntity,
             renderer='json', permission='paste')
def paste(context, request):
    schema = IdListSchema(context={
        'request': request,
        'folder': context.entity
    })

    form_data = request.POST.mixed()

    try:
        result = schema.load(form_data)
        context.paste(result['ids'])
        return {'pasted': True}
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)
    except PasteError as error:
        raise HTTPInternalServerError(error)
