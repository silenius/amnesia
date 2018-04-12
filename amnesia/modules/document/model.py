# -*- coding: utf-8 -*-

from sqlalchemy.ext.hybrid import hybrid_property

from ..content import Content
from ..content import ContentTranslation


class DocumentTranslation(ContentTranslation):
    ''' Holds translations '''


class Document(Content):
    ''' A document '''

    @hybrid_property
    def body(self):
        return self.current_translation.body

    @body.setter
    def body(self, value):
        self.current_translation.body = value

