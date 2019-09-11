# -*- coding: utf-8 -*-

from marshmallow.fields import String
from marshmallow.fields import Integer
from marshmallow.fields import Raw
from marshmallow.fields import Float

from amnesia.modules.content.validation import ContentSchema


class FileSchema(ContentSchema):
    ''' Schema for the File model '''

    content_id = Integer()
    mime_id = Integer(dump_only=True)
    original_name = String(dump_only=True)
    file_size = Float(dump_only=True)
    content = Raw(load_only=True)
