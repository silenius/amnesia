from marshmallow import Schema
from marshmallow.fields import Nested
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Dict

class MimeMajor(Schema):
    id = Integer(dump_only=True)
    name = String()
    icons = Dict()


class Mime(Schema):
    id = Integer(dump_only=True)
    name = String()
    template = String()
    major_id = Integer(dump_only=True)
    major = Nested(MimeMajor, dump_only=True)
    icons = Dict()
    ext = String()
