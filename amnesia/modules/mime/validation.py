from marshmallow import Schema
from marshmallow.fields import Nested
from marshmallow.fields import Integer
from marshmallow.fields import String

class MimeMajor(Schema):
    id = Integer(dump_only=True)
    name = String()
    icon = String()


class Mime(Schema):
    id = Integer(dump_only=True)
    name = String()
    template = String()
    major_id = Integer(dump_only=True)
    major = Nested(MimeMajor, dump_only=True)
    icon = String()
    ext = String()
