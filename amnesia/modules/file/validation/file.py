from marshmallow import pre_load

from marshmallow.fields import String
from marshmallow.fields import Integer
from marshmallow.fields import Raw
from marshmallow.fields import Float
from marshmallow.fields import Nested

from amnesia.modules.content.validation import ContentSchema
from amnesia.modules.mime.validation import Mime


class FileSchema(ContentSchema):
    ''' Schema for the File model '''

    content_id = Integer(dump_only=True)
    mime_id = Integer(dump_only=True)
    original_name = String(dump_only=True)
    file_size = Float(dump_only=True)
    content = Raw(load_only=True, required=True)
    mime = Nested(Mime, dump_only=True)

    @pre_load
    def _pre_content(self, data, **kwargs):
        if self.context['request'].method in ['PUT']:
            content = self.fields['content']
            content.required = False
            content.allow_none = True

        return data
