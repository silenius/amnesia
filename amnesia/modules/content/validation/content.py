# -*- coding: utf-8 -*-

# pylint: disable=invalid-name,no-member

import logging

from datetime import date
from datetime import datetime

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_dump
from marshmallow import post_load
from marshmallow import pre_load
from marshmallow import ValidationError

from marshmallow.fields import Boolean
from marshmallow.fields import DateTime
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Nested
from marshmallow.fields import List

from marshmallow.validate import Range
from marshmallow.validate import OneOf

from sqlalchemy import sql

from amnesia.utils.validation import PyramidContextMixin
from amnesia.utils.validation import as_list
from amnesia.utils.validation.fields import JSON
from amnesia.modules.folder import Folder
from amnesia.modules.tag import Tag
from amnesia.modules.state import State
from amnesia.modules.tag.validation import TagSchema
from amnesia.modules.content_type.validation import ContentTypeSchema

log = logging.getLogger(__name__)


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
    weight = Integer(dump_only=True)
    content_type_id = Integer(dump_only=True)
    type = Nested(ContentTypeSchema, dump_only=True)
    container_id = Integer(dump_only=True)
    owner_id = Integer(dump_only=True)
    state_id = Integer(dump_only=True)
    on_success = Integer(default=201, missing=201, validate=OneOf((201, 303)))

    tags_id = List(Integer(), load_only=True)
    tags = Nested(TagSchema, many=True, dump_only=True)

    inherits_parent_acl = Boolean(missing=True)

    props = JSON(missing=None, default=None)

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
    def pre_load_process(self, data, **kwargs):
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
    def post_load_process(self, item, **kwargs):
        if 'tags_id' in item:
            filters = Tag.id.in_(item.pop('tags_id'))
            stmt_tags = sql.select(Tag).filter(filters)
            item['tags'] = self.dbsession.execute(stmt_tags).scalars().all()

        if 'container_id' in item:
            item['parent'] = self.dbsession.get(Folder, item.pop('container_id'))

        stmt_state = sql.select(State).filter_by(name='published')
        item['state'] = self.dbsession.execute(stmt_state).scalar_one()

        entity = self.context.get('entity')
        has_permission = self.context['request'].has_permission
        if not has_permission('manage_acl'):
            k = 'inherits_parent_acl'
            # Update
            if entity:
                if item[k] != entity.inherits_parent_acl:
                    raise ValidationError('Inherits ACL: permission denied')
            # Create
            else:
                if k in item:
                    del item[k]

        return item

    ########
    # DUMP #
    ########

    @post_dump(pass_original=True)
    def post_dump_process(self, data, orig, **kwargs):
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

        #data['tags_id'] = [i['id'] for i in data['tags']]

        return data


class IdListSchema(Schema):
    ids = List(Integer(validate=Range(min=1)), required=True)

    @pre_load
    def ensure_list(self, data, **kwargs):
        try:
            data['ids'] = as_list(data['ids'])
        except KeyError:
            data['ids'] = []

        return data
