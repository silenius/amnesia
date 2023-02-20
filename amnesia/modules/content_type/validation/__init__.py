from marshmallow import Schema
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Dict


class ContentTypeSchema(Schema):

    id = Integer(dump_only=True)
    name = String()
    icon = String()
    description = String()
    icons = Dict()
