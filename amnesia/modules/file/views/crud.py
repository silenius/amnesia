# -*- coding: utf-8 -*-

import logging
import os
import os.path
import pathlib
import shutil

import magic

from hashids import Hashids

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
from amnesia.modules.file import FileEntity
from amnesia.modules.file.validation import FileSchema
from amnesia.modules.file.events import FileUpdated
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(context=FileEntity, name='download', request_method='GET',
             permission='read')
def download(context, request):
    file_response = context.serve()

    if not file_response:
        return HTTPNotFound()

    return file_response


def save_file(request, entity, data):
    settings = request.registry.settings

    input_file = data['content'].file
    input_file_name = data['content'].filename
    entity.original_name = input_file_name

    dirname = settings['file_storage_dir']
    salt = settings['amnesia.hashid_file_salt']

    if entity.id and input_file:
        hashid = Hashids(salt=salt, min_length=8)
        log.debug('===>>> save_file: %s', entity.path_name)
        hid = hashid.encode(entity.path_name)

        file_name = pathlib.Path(
            dirname,
            *(hid[:4]),
            hid + entity.extension
        )

        if not file_name.parent.exists():
            file_name.parent.mkdir(parents=True)

        # Ensure that the current file position of the input file is 0 (= we
        # are at the begining of the file)
        input_file.seek(0)
        with open(file_name, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

            # Close both files, to ensure buffers are flushed
            input_file.close()
            output_file.close()

        # A file must be associated to a MIME type (image/png,
        # application/pdf, etc). Rather than trusting the extension of the
        # file, we use the magic number instead. The magic number approach
        # offers better guarantees that the format will be identified
        # correctly.
        file_magic = magic.detect_from_filename(file_name)
        mime_type = file_magic.mime_type
        major, minor = mime_type.split('/')

        # Fetch mime from database
        mime_obj = Mime.q_major_minor(request.dbsession, major, minor)

        entity.mime = mime_obj

        # bytes -> megabytes
        entity.file_size = os.path.getsize(file_name) / 1024.0 / 1024.0

        return entity

    return False


class FileCRUD(ContentCRUD):
    """ File CRUD """

    form_tmpl = 'amnesia:templates/file/_form.pt'

    @view_config(context=FileEntity, request_method='GET', name='edit',
                 renderer='amnesia:templates/file/edit.pt')
    def edit(self):
        schema = FileSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        return self.edit_form(data)

    @view_config(request_method='GET', name='add_file',
                 renderer='amnesia:templates/file/edit.pt',
                 context=FolderEntity, permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data, view='@@add_file')

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(request_method='GET', renderer='json',
                 accept='application/json', permission='read',
                 context=FileEntity)
    def read_json(self):
        schema = FileSchema(context={'request': self.request})
        return schema.dump(self.context.entity, many=False)

    @view_config(request_method='GET',
                 renderer='amnesia:templates/file/show.pt',
                 accept='text/html', permission='read',
                 context=FileEntity)
    def read_html(self):
        return super().read()

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/file/edit.pt',
                 context=FolderEntity,
                 name='add_file',
                 permission='create')
    def create(self):
        form_data = self.request.POST.mixed()
        schema = FileSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return self.edit_form(form_data, error.messages, view='@@add_file')

        data.update({
            'file_size': 0,
            'mime_id': -1,
            'original_name': ''
        })

        new_entity = self.context.create(File, data)

        if new_entity:
            save_file(self.request, new_entity, data)
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
                 context=FileEntity,
                 permission='edit')
    def update(self):
        form_data = self.request.POST.mixed()
        schema = FileSchema(
            context={'request': self.request},
            exclude=('container_id', )
        )

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages)

        data.update({
            'file_size': self.entity.file_size,
            'mime_id': self.entity.mime_id,
            'original_name': self.entity.original_name
        })

        updated_entity = self.context.update(data)
        evt = FileUpdated(self.request, self.entity)
        self.request.registry.notify(evt)

        if updated_entity:
            if isinstance(data['content'], cgi_FieldStorage):
                save_file(self.request, updated_entity, data)

            return HTTPFound(location=self.request.resource_url(updated_entity))
