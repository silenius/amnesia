from marshmallow import validates_schema
from marshmallow import ValidationError
from marshmallow.fields import Integer
from marshmallow.fields import Float
from marshmallow.fields import String
from marshmallow.fields import DateTime
from marshmallow.fields import Email
from marshmallow.fields import Nested
from marshmallow.validate import Length

from amnesia.modules.content.validation import ContentSchema
from amnesia.modules.country import CountrySchema


class EventSchema(ContentSchema):
    ''' Schema for the Event model '''

    content_id = Integer()
    body = String()
    location = String(allow_none=True)
    address = String(allow_none=True)
    address_latitude = Float(allow_none=True)
    address_longitude = Float(allow_none=True)
    attendees = String(allow_none=True)
    contact_name = String(allow_none=True)
    contact_email = Email(allow_none=True)
    contact_phone = String(allow_none=True)
    country_iso = String(allow_none=True, validate=Length(equal=2))
    country = Nested(CountrySchema, dump_only=True)

    starts = DateTime('%Y-%m-%d %H:%M', required=True)
    ends = DateTime('%Y-%m-%d %H:%M', required=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if 'ends' in data and 'starts' in data and data['ends'] < data['starts']:
            raise ValidationError('End date must be greater than Start date')
