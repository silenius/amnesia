import logging

from marshmallow import Schema
from marshmallow.fields import (
    String,
    Integer
)

log = logging.getLogger(__name__)


class StateSchema(Schema):

    id = Integer(dump_only=True)
    name = String()
    description = String(missing=None)
