# -*- coding: utf-8 -*-

from marshmallow import Schema

from marshmallow.fields import Integer
from marshmallow.fields import String

from amnesia.utils.validation import PyramidContextMixin


class TagSchema(Schema, PyramidContextMixin):

    id = Integer(dump_only=True)
    name = String(required=True)
    description = String()
