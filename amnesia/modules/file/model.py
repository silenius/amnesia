# -*- coding: utf-8 -*-

# pylint: disable=E1101

import os.path

from amnesia.modules.content import Content


class File(Content):

    def feed(self, **kwargs):
        for c in ('file_size', 'mime_id', 'original_name'):
            if c in kwargs:
                setattr(self, c, kwargs.pop(c))

        super().feed(**kwargs)

    @property
    def fa_icon(self):
        if self.mime.major.name == 'image':
            return 'fa-file-image-o'
        if self.mime.major.name == 'video':
            return 'fa-file-video-o'
        if self.mime.full == 'application/pdf':
            return 'fa-file-pdf-o'
        return super().fa_icon

    @property
    def extension(self):
        return os.path.splitext(self.original_name)[1].lower()
