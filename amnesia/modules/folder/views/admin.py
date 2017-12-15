# -*- coding: utf-8 -*-

# pylint: disable=E1101

import json

from pyramid.view import view_config

from amnesia.modules.content_type import ContentType


def includeme(config):
    config.scan(__name__)


@view_config(request_method='GET', name='admin',
             renderer='amnesia:templates/folder/show/admin.pt')
def admin(context, request):
    try:
        content = context.entity
        if content.type.name != 'folder':
            content = content.parent
    except AttributeError:
        content = request.registry['root_folder']
        #request.dbsession.add(content)

    session = request.session
    copy_oids = json.dumps(session.get('copy_oids', []))
    content_types = request.dbsession.query(ContentType).all()

    return {
        'content': content,
        'copy_oids': copy_oids,
        'content_types': content_types
    }
