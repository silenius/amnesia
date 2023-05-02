import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.folder import FolderEntity
from amnesia.modules.document import Document
from amnesia.modules.document import DocumentEntity
from amnesia.modules.document.validation import DocumentSchema

from ...content.views import ContentCRUD

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__, categories=('pyramid', 'amnesia'))
    #config.scan(__name__)


@view_defaults(context=DocumentEntity)
class DocumentCRUD(ContentCRUD):
    ''' Document CRUD '''

    ########
    # POST #
    ########

    @view_config(
        request_method='POST',
        renderer='json',
        context=FolderEntity,
        name='add_document',
        permission='create'
    )
    def create(self):
        ''' Create a new Document '''

        form_data = self.request.POST.mixed()
        schema = self.schema(DocumentSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        new_entity = self.context.create(Document, data)

        if new_entity:
            self.request.response.status_int = 201
            return schema.dump(new_entity)

        raise HTTPInternalServerError()

    #######
    # PUT #
    #######

    @view_config(
        request_method='PUT',
        renderer='json',
        permission='edit'
    )
    def put(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(DocumentSchema, exclude={'acls'})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        document = self.context.update(data)

        if not document:
            raise HTTPInternalServerError()

        location = self.request.resource_url(document)

        return HTTPNoContent(location=location)

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read',
    )
    def read_json(self):
        return self.schema(DocumentSchema).dump(self.entity)
