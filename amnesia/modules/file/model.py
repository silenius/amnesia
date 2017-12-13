# -*- coding: utf-8 -*-

# pylint: disable=E1101

import os.path

from amnesia.modules.content import Content


class File(Content):

    @property
    def fa_icon(self):
        if self.mime.major.name == 'image':
            return 'fa-file-image-o'
        elif self.mime.major.name == 'video':
            return 'fa-file-video-o'
        elif self.mime.full == 'application/pdf':
            return 'fa-file-pdf-o'
        else:
            return super().fa_icon

    @property
    def extension(self):
        return os.path.splitext(self.original_name)[1].lower()

    @property
    def filename(self):
        return '{0}{1}'.format(self.id, self.extension)

    @property
    def subpath(self):
        return os.path.join(*((str(self.id))[0:3].zfill(3)))
