from marshmallow import (
    Schema,
    EXCLUDE
)

from marshmallow.fields import (
    Integer
)

from marshmallow.validate import (
    Range
)

class PaginationSchema(Schema):
    limit = Integer(validate=Range(min=1, max=100), missing=50)
    offset = Integer(validate=Range(min=0), missing=0)

    class Meta:
        unknown = EXCLUDE
