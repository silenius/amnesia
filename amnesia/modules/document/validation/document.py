# -*- coding: utf-8 -*-


from marshmallow.fields import Integer
from marshmallow.fields import String

from amnesia.modules.content.validation import ContentSchema


class DocumentSchema(ContentSchema):
    ''' Schema for the Document model '''

    content_id = Integer(dump_only=True)
    body = String()
