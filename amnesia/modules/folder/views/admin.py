# -*- coding: utf-8 -*-

# pylint: disable=E1101

import json

from pyramid.view import view_config

from amnesia.modules.folder import FolderEntity
from amnesia.modules.content_type import ContentType


def includeme(config):
    config.scan(__name__)


@view_config(request_method='GET', name='admin', context=FolderEntity,
             renderer='amnesia:templates/folder/show/admin.pt')
def admin(context, request):
    content = context.entity
    copy_oids = json.dumps(request.session.get('copy_oids', []))
    content_types = request.dbsession.query(ContentType).all()

    return {
        'content': content,
        'copy_oids': copy_oids,
        'content_types': content_types
    }
