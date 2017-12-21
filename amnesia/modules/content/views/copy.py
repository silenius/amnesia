# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.content.validation import IdListSchema
from amnesia.modules.content import SessionResource


def includeme(config):
    ''' Pyramid includeme '''
    config.scan(__name__)


@view_config(name='scopy', request_method='POST',
             renderer='json', context=SessionResource,
             permission='copy')
def copy_oids_to_session(context, request):
    ''' Copy oids to session '''
    result, errors = IdListSchema().load(request.POST.mixed())

    if errors:
        raise HTTPInternalServerError()

    oids = context.copy_oids(result['oid'])

    return {'oids': oids}


@view_config(name='sremove', request_method='POST',
             renderer='json', context=SessionResource,
             permission='delete')
def remove_oids_from_session(context, request):
    ''' Clear the session oids '''
    removed = context.clear_oids()
    return {'removed': removed}
