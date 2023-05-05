from marshmallow import Schema
from marshmallow.fields import String


class CountrySchema(Schema):

    name = String()
    iso = String()
