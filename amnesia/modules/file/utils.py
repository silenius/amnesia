import logging
import os.path
import pathlib
import shutil
import typing as t

import magic

from pyramid.request import Request
from webob.compat import cgi_FieldStorage

from amnesia.modules.file import File
from amnesia.modules.file.events import FileSavedToDisk
from amnesia.modules.mime.utils import fetch_mime

log = logging.getLogger(__name__)


def save_to_disk(request: Request, entity: File, src: cgi_FieldStorage) -> \
        t.Union[File, t.Literal[False]]:
    settings = request.registry.settings

    input_file = src.file
    # IE sends an absolute file *path* as the filename.
    input_file_name = pathlib.Path(src.filename).name
    entity.original_name = input_file_name

    dirname = settings['file_storage_dir']
    salt = settings['amnesia.hashid_file_salt']

    if entity.content_id and input_file:
        log.debug('===>>> save_file: %s', entity.path_name)
        hid = entity.get_hashid(salt=salt)

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
        mime_obj = fetch_mime(request.dbsession, major, minor)

        entity.mime = mime_obj

        # bytes -> megabytes
        entity.file_size = os.path.getsize(file_name) / 1024.0 / 1024.0

        event = FileSavedToDisk(request, entity, file_name)
        request.registry.notify(event)

        return entity

    return False

