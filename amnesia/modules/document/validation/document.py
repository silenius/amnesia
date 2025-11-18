from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Boolean

from amnesia.modules.content.validation import ContentSchema


class DocumentSchema(ContentSchema):
    ''' Schema for the Document model '''

    content_id = Integer(dump_only=True)
    body = String()
    is_block = Boolean()
