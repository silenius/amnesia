# -*- coding: utf-8 -*-

import logging
import os
import os.path
import shutil
import unicodedata

import magic

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from webob.compat import cgi_FieldStorage

from amnesia.modules.mime import Mime
from amnesia.modules.folder import FolderEntity
from amnesia.modules.file import File
from amnesia.modules.file import FileEntity
from amnesia.modules.file import FileResource
from amnesia.modules.file.validation import FileSchema
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

    file_name, file_ext = os.path.splitext(context.entity.original_name)
    file_name = ''.join(s for s in file_name if s.isalnum()) + file_ext
    # Important: HTTP headers should (must) be ASCII!
    file_name = unicodedata.normalize('NFKD', file_name).\
        encode('ascii', 'ignore').decode('ascii')
    disposition = '{0}; filename="{1}"'.format('attachment', file_name)
    file_response.headers.add('Content-Disposition', disposition)

    return file_response


def save_file(request, entity, data):
    input_file = data['content'].file
    input_file_name = data['content'].filename
    entity.original_name = input_file_name

    storage_dir = request.registry.settings.get('file_storage_dir')
    if entity.id and input_file:
        # To avoid thousands of files in the same directory (which is bad),
        # we take the first three digits of the primary key separately (or
        # zero filled if < 100), each digit will be a directory, for
        # example (where "->" means "will be stored"):
        # - content_id == 5     -> 0/0/5/5.ext
        # - content_id == 24    -> 0/2/4/24.ext
        # - content_id == 153   -> 1/5/3/153.ext
        # - content_id == 1536  -> 1/5/3/1536.ext
        # - ...
        file_directory = os.path.join(storage_dir, entity.subpath)

        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        full_file_name = os.path.join(file_directory, entity.filename)

        # Copy the uploaded file to it's final destination
        input_file.seek(0)
        with open(full_file_name, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

            # Close both files, to ensure buffers are flushed
            input_file.close()
            output_file.close()

        # A file must be associated to a MIME type (image/png,
        # application/pdf, etc). Rather than trusting the extension of the
        # file, we use the magic number instead. The magic number approach
        # offers better guarantees that the format will be identified
        # correctly.
        file_magic = magic.detect_from_filename(full_file_name)
        mime_type = file_magic.mime_type
        major, minor = mime_type.split('/')

        # Fetch mime from database
        mime_obj = Mime.q_major_minor(request.dbsession, major, minor)

        entity.mime = mime_obj

        # bytes -> megabytes
        entity.file_size = os.path.getsize(full_file_name) / 1024.0 / 1024.0

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
            return self.edit_form(form_data, error.messages, view='@@add_file')

        data.update({
            'file_size': 0,
            'mime_id': -1,
            'original_name': ''
        })

        # The primary key of file_obj will be used for the filename (so that it
        # ensures uniqueness). If it's a new file_obj (so no id yet) we have to
        # insert it first in the database (to get a new id), so the idea if to
        # flush but don't COMMIT until the file is saved on disk.
        # NOTE: the "fk_mime" constraint is marked DEFERRABLE INITIALLY DEFERRED
        new_entity = self.context.create(File, data)

        if new_entity:
            save_file(self.request, new_entity, data)
            return HTTPFound(location=self.request.resource_url(new_entity))

        return self.edit_form(form_data, view='@@add_file')

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/document/edit.pt',
                 context=FileEntity)
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

        updated_entity = self.context.update(data)

        if updated_entity:
            if isinstance(data['content'], cgi_FieldStorage):
                save_file(self.request, updated_entity, data)
            return HTTPFound(location=self.request.resource_url(updated_entity))
