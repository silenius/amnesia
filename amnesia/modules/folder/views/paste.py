# -*- coding: utf-8 -*-

# pylint: disable=E1101

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError

from amnesia.modules.content.validation import IdListSchema
from amnesia.modules.content import Content
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder.exc import PasteError


def includeme(config):
    config.scan(__name__)


@view_config(request_method='POST', name='paste', context=FolderEntity,
             renderer='json', permission='paste')
def paste(context, request):
    try:
        result = IdListSchema().load(request.POST.mixed())
        context.paste(result['oid'])
        return {'pasted': True}
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)
    except PasteError as error:
        raise HTTPInternalServerError(error)
