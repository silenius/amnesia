# -*- coding: utf-8 -*-

# pylint: disable=E1101

from datetime import date
from datetime import datetime

from marshmallow import pre_load
from marshmallow import post_load
from marshmallow import post_dump

from marshmallow.fields import Integer
from marshmallow.fields import Float
from marshmallow.fields import String
from marshmallow.fields import DateTime
from marshmallow.fields import Email
from marshmallow.validate import Length
from marshmallow.validate import Range

from amnesia.modules.content.validation import ContentSchema


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

    starts = DateTime(required=True, dump_only=True)
    ends = DateTime(required=True, dump_only=True)

    starts_year = Integer(load_only=True)
    starts_month = Integer(load_only=True, validate=Range(min=1, max=12))
    starts_day = Integer(load_only=True, validate=Range(min=1, max=31))
    starts_hour = Integer(load_only=True, allow_none=True,
                          validate=Range(min=0, max=23))
    starts_minute = Integer(load_only=True, allow_none=True,
                            validate=Range(min=0, max=55))

    ends_year = Integer(load_only=True)
    ends_month = Integer(load_only=True, validate=Range(min=1, max=12))
    ends_day = Integer(load_only=True, validate=Range(min=1, max=31))
    ends_hour = Integer(load_only=True, allow_none=True,
                        validate=Range(min=0, max=23))
    ends_minute = Integer(load_only=True, allow_none=True,
                          validate=Range(min=0, max=55))

    ########
    # LOAD #
    ########

    @post_load
    def load_event_dates(self, data):
        # Starts / Ends
        for part in ('starts', 'ends'):
            date_col = (part + '_year', part + '_month', part + '_day')
            time_col = (part + '_hour', part + '_minute')

            if all((data.get(i) for i in date_col)):
                col = [int(data[i]) for i in date_col]
                if all((data.get(i) for i in time_col)):
                    col.extend([int(data[i]) for i in time_col])

                data[part] = datetime(*col).isoformat()

        return data

    ########
    # DUMP #
    ########

    @post_dump(pass_original=True)
    def split_event_dates(self, data, orig):
        # Effective / Expiration dates
        date_col = ('year', 'month', 'day')
        datetime_col = ('year', 'month', 'day', 'hour', 'minute')

        for col in ('starts', 'ends'):
            value = getattr(orig, col)
            if isinstance(value, datetime):
                for i in datetime_col:
                    data['{}_{}'.format(col, i)] = getattr(value, i)
            elif isinstance(value, date):
                for i in date_col:
                    data['{}_{}'.format(col, i)] = getattr(value, i)

        return data
