# -*- coding: utf-8 -*-

import json

from marshmallow import fields

class JSON(fields.Dict):

    def _deserialize(self, value, attr, data):
        decoded = json.loads(value)
        return super()._deserialize(decoded, attr, data)

    def _serialize(self, value, attr, obj):
        ret = super()._serialize(value, attr, obj)
        return json.dumps(ret)
