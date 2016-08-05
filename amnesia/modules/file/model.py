# -*- coding: utf-8 -*-

import os
import os.path

from .content import Content

class File(Content):

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)

    @property
    def extension(self):
        return os.path.splitext(self.original_name)[1].lower()

    @property
    def filename(self):
        return '%s%s' % (self.id, self.extension)

    @property
    def subpath(self):
        return os.path.join(*((str(self.id))[0:3].zfill(3)))

    def type_icon(self, size='16x16'):
        if self.mime.major.icon:
            if self.mime.icon:
                return cherrypy.url('/images/mimes/%s/%s/%s' %\
                       (size, self.mime.major.name, self.mime.icon))
            return cherrypy.url('/images/mimes/%s/%s' %\
                   (size, self.mime.major.icon))
        return cherrypy.url('/images/content_types/%s/%s' %\
               (size, self.type.icon))
