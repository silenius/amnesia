# -*- coding: utf-8 -*-

# pylint: disable=E1101

import json

from datetime import date
from datetime import datetime

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_dump
from marshmallow import post_load
from marshmallow import pre_load

from marshmallow.fields import Boolean
from marshmallow.fields import DateTime
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Nested
from marshmallow.fields import List
from marshmallow.fields import Function

from marshmallow.validate import Range

from amnesia.utils.validation import PyramidContextMixin
from amnesia.utils.validation import as_list
from amnesia.modules.tag import Tag
from amnesia.modules.tag.validation import TagSchema
from amnesia.modules.content_type.validation import ContentTypeSchema


class ContentSchema(Schema, PyramidContextMixin):
    """Base class for Content validation"""

    id = Integer(dump_only=True)
    added = DateTime(dump_only=True)
    updated = DateTime(dump_only=True)
    title = String()
    description = String(missing=None)
    effective = DateTime()
    expiration = DateTime()
    exclude_nav = Boolean(missing=False)
    is_fts = Boolean(missing=False)
    weight = Integer()
    content_type_id = Integer(dump_only=True)
    type = Nested(ContentTypeSchema, dump_only=True)
    container_id = Integer(required=False, missing=None)
    owner_id = Integer(dump_only=True)
    state_id = Integer(dump_only=True)

    tags_id = List(Integer(), load_only=True)
    tags = Nested(TagSchema, many=True, dump_only=True)

    inherits_parent_acl = Boolean(missing=True)

    props = Function(lambda obj: json.dumps(obj.props),
                     lambda obj: json.loads(obj), required=False)

    # XXX: remvoe this and use ISO format
    effective_year = Integer(load_only=True, required=False, allow_none=True)
    effective_month = Integer(load_only=True, required=False, allow_none=True)
    effective_day = Integer(load_only=True, required=False, allow_none=True)
    effective_hour = Integer(load_only=True, required=False, allow_none=True)
    effective_minute = Integer(load_only=True, required=False, allow_none=True)

    # XXX: remvoe this and use ISO format
    expiration_year = Integer(load_only=True, required=False, allow_none=True)
    expiration_month = Integer(load_only=True, required=False, allow_none=True)
    expiration_day = Integer(load_only=True, required=False, allow_none=True)
    expiration_hour = Integer(load_only=True, required=False, allow_none=True)
    expiration_minute = Integer(load_only=True, required=False, allow_none=True)

    class Meta:
        unknown = EXCLUDE

    ########
    # LOAD #
    ########

    @pre_load
    def pre_process(self, data):
        _data = {k: None if v == '' else v for k, v in data.items()}

        # Starts / Ends
        for part in ('effective', 'expiration'):
            date_col = (part + '_year', part + '_month', part + '_day')
            time_col = (part + '_hour', part + '_minute')

            if all((_data.get(i) for i in date_col)):
                col = [int(_data[i]) for i in date_col]
                if all((_data.get(i) for i in time_col)):
                    col.extend([int(_data[i]) for i in time_col])

                _data[part] = datetime(*col).isoformat()

        # Tags
        try:
            _data['tags_id'] = as_list(_data['tags_id'])
        except KeyError:
            _data['tags_id'] = []

        return _data

    @post_load
    def load_tags(self, item):
        if 'tags_id' in item:
            filters = Tag.id.in_(item['tags_id'])
            item['tags'] = self.dbsession.query(Tag).filter(filters).all()
        return item

    ########
    # DUMP #
    ########

    @post_dump
    def post_dump_adapt_tags(self, data):
        data['tags_id'] = [i['id'] for i in data['tags']]
        return data

    @post_dump(pass_original=True)
    def post_dump_adapt_dates(self, data, orig):
        # Effective / Expiration dates
        date_col = ('year', 'month', 'day')
        datetime_col = ('year', 'month', 'day', 'hour', 'minute')

        for col in ('effective', 'expiration'):
            value = getattr(orig, col, None)
            if isinstance(value, datetime):
                for i in datetime_col:
                    data['{}_{}'.format(col, i)] = getattr(value, i)
            elif isinstance(value, date):
                for i in date_col:
                    data['{}_{}'.format(col, i)] = getattr(value, i)

        return data


class IdListSchema(Schema):
    oid = List(Integer(validate=Range(min=1)), required=True)

    @pre_load
    def ensure_list(self, data):
        try:
            data['oid'] = as_list(data['oid'])
        except KeyError:
            data['oid'] = []

        return data
