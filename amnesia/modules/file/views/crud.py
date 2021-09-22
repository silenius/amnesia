import logging
import os
import os.path
import pathlib
import shutil

import magic

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPInternalServerError

from webob.compat import cgi_FieldStorage

from amnesia.modules.mime import Mime
from amnesia.modules.folder import FolderEntity
from amnesia.modules.file import File
from amnesia.modules.file import utils as file_utils
from amnesia.modules.file import FileEntity
from amnesia.modules.file.validation import FileSchema
from amnesia.modules.file.forms import FileForm
from amnesia.modules.file.events import FileUpdated
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(
    context=FileEntity,
    name='download',
    request_method='GET',
    permission='read'
)
def download(context, request):
    file_response = context.serve()

    if not file_response:
        return HTTPNotFound()

    return file_response


class FileCRUD(ContentCRUD):
    """ File CRUD """

    @view_config(context=FileEntity, request_method='GET', name='edit',
                 renderer='amnesia:templates/file/edit.pt')
    def edit(self):
        schema = FileSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        form = FileForm(self.request)
        action = self.request.resource_path(self.context)

        return {
            'form': form.render(data),
            'form_action': action
        }

    @view_config(request_method='GET', name='add_file',
                 renderer='amnesia:templates/file/edit.pt',
                 context=FolderEntity, permission='create')
    def new(self):
        data = self.request.GET.mixed()
        form = FileForm(self.request)
        action = self.request.resource_path(self.context, '@@add_file')

        return {
            'form': form.render(data),
            'form_action': action
        }

    #########################################################################
    # (C)RUD - CREATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/file/edit.pt',
        context=FolderEntity,
        name='add_file',
        permission='create'
    )
    def create(self):
        form_data = self.request.POST.mixed()
        schema = FileSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            form = FileForm(self.request)
            form_action = self.request.resource_path(
                self.context, '@@add_file'
            )

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

        data.update({
            'file_size': 0,
            'mime_id': -1,
            'original_name': ''
        })

        new_entity = self.context.create(File, data)

        if new_entity:
            file_utils.save_to_disk(self.request, new_entity, data)
            location = self.request.resource_url(new_entity)
            http_code = data['on_success']
            if http_code == 201:
                return HTTPCreated(location=location)
            if http_code == 303:
                return HTTPSeeOther(location=location)

        raise HTTPInternalServerError()


    #########################################################################
    # C(R)UD - READ                                                         #
    #########################################################################

    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read',
        context=FileEntity
    )
    def read_json(self):
        schema = FileSchema(context={'request': self.request})
        return schema.dump(self.context.entity, many=False)

    @view_config(
        request_method='GET',
        renderer='amnesia:templates/file/show.pt',
        accept='text/html',
        permission='read',
        context=FileEntity
    )
    def read_html(self):
        return super().read()

    #########################################################################
    # CR(U)D - UPDATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/file/edit.pt',
        context=FileEntity,
        permission='edit'
    )
    def update(self):
        form_data = self.request.POST.mixed()
        schema = FileSchema(
            context={'request': self.request},
            exclude=('container_id', )
        )

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            form = FileForm(self.request)
            form_action = self.request.resource_path(self.context)

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

        data.update({
            'file_size': self.entity.file_size,
            'mime_id': self.entity.mime_id,
            'original_name': self.entity.original_name
        })

        updated_entity = self.context.update(data)

        if updated_entity:
            evt = FileUpdated(self.request, self.entity)
            self.request.registry.notify(evt)
            if isinstance(data['content'], cgi_FieldStorage):
                file_utils.save_to_disk(self.request, updated_entity, data)

            return HTTPFound(location=self.request.resource_url(updated_entity))

        raise HTTPInternalServerError()
