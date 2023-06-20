import logging
import json

from marshmallow import fields

log = logging.getLogger(__name__)


class JSON(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return json.loads(value)
        except ValueError:
            return None
