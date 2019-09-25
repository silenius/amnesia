# -*- coding: utf-8 -*-

import logging
import json

from marshmallow import fields

log = logging.getLogger(__name__)


class JSON(fields.Dict):

    def _deserialize(self, value, attr, data, **kwargs):
        decoded = json.loads(value)

        if not decoded:
            return None

        return super()._deserialize(decoded, attr, data, **kwargs)

    def _serialize(self, value, attr, obj):
        ret = super()._serialize(value, attr, obj)
        return json.dumps(ret)
