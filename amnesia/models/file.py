# -*- coding: utf-8 -*-

import os
import os.path

import cherrypy

from amnesia import db
from amnesia.models import content


class FileQuery(content.ContentQuery):

    def __init__(self, *args, **kwargs):
        super(FileQuery, self).__init__(*args, **kwargs)


class File(content.Content):

    query = db.Session.query_property(FileQuery)

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
                       (size, self.mime.major.major, self.mime.icon))
            return cherrypy.url('/images/mimes/%s/%s' %\
                   (size, self.mime.major.icon))
        return cherrypy.url('/images/content_types/%s/%s' %\
               (size, self.type.icon))
