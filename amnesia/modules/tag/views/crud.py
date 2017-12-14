# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError

from sqlalchemy import orm

from amnesia import order

from amnesia.modules.tag import TagEntity
from amnesia.modules.tag import TagResource
from amnesia.modules.content.views import ContentCRUD


def includeme(config):
    config.scan(__name__)


class TagCRUD(ContentCRUD):
    """ Tag CRUD """

    @property
    def schema(self):
        return self.context.get_validation_schema()

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='json',
                 context=TagResource)
    def create(self):
        form_data = self.request.POST.mixed()
        data, errors = self.schema.load(form_data)

        if errors:
            raise HTTPInternalServerError()

        new_entity = self.context.create(data)

        if new_entity:
            location = self.request.resource_url(self.context, new_entity.id)
            return HTTPFound(location=location)

        raise HTTPInternalServerError()

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(context=TagEntity, request_method='GET', name='',
                 renderer='json')
    def read(self):
        return {
            'id': self.entity.id,
            'name': self.entity.name,
            'description': self.entity.description
        }
