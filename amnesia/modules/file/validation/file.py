import pathlib

from marshmallow import (
    pre_load,
    post_load
)

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

    @post_load
    def original_name(self, data, **kwargs):
        # IE sends an absolute file *path* as the filename.
        method = self.context['request'].method
        
        if method == 'POST' or (method == 'PUT' and data['content'] is not None):
            data['original_name'] = pathlib.Path(data['content'].filename).name
        
        return data
