# -*- coding: utf-8 -*-

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.folder import FolderEntity
from amnesia.modules.document import Document
from amnesia.modules.document import DocumentEntity
from amnesia.modules.document.validation import DocumentSchema

from ...content.views import ContentCRUD

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class DocumentCRUD(ContentCRUD):
    ''' Document CRUD '''

    form_tmpl = 'amnesia:templates/document/_form.pt'

    @view_config(request_method='GET', name='edit',
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentEntity,
                 permission='edit')
    def edit(self):
        data = DocumentSchema().dump(self.entity)
        return self.edit_form(data)

    @view_config(request_method='GET', name='add_document',
                 renderer='amnesia:templates/document/edit.pt',
                 context=FolderEntity,
                 permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data, view='@@add_document')

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(request_method='GET', renderer='json',
                 accept='application/json', permission='read',
                 context=DocumentEntity)
    def read_json(self):
        schema = DocumentSchema(context={
            'request': self.request
        })

        return schema.dump(self.context.entity)

    @view_config(request_method='GET',
                 renderer='amnesia:templates/document/show.pt',
                 accept='text/html', permission='read',
                 context=DocumentEntity)
    def read_html(self):
        return super().read()

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/document/edit.pt',
                 context=FolderEntity,
                 name='add_document',
                 permission='create')
    def create(self):
        ''' Create a new Document '''

        form_data = self.request.POST.mixed()
        schema = DocumentSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return self.edit_form(form_data, error.messages,
                                  view='@@add_document')

        new_entity = self.context.create(Document, data)

        if new_entity:
            location = self.request.resource_url(new_entity)
            http_code = data['on_success']
            if http_code == 201:
                return HTTPCreated(location=location)
            if http_code == 303:
                return HTTPSeeOther(location=location)

        raise HTTPInternalServerError()

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentEntity,
                 permission='edit')
    def update(self):
        form_data = self.request.POST.mixed()
        schema = DocumentSchema(context={
            'request': self.request
        }, exclude=('container_id', ))

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages)

        updated_entity = self.context.update(data)

        if updated_entity:
            location = self.request.resource_url(updated_entity)
            return HTTPFound(location=location)
