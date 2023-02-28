# pylint: disable=E1101

import json

from marshmallow import Schema
from marshmallow import post_dump
from marshmallow import pre_load
from marshmallow import post_load

from marshmallow.fields import Integer
from marshmallow.fields import Boolean
from marshmallow.fields import String
from marshmallow.fields import Nested
from marshmallow.fields import List

from marshmallow.validate import OneOf

from sqlalchemy import sql

from amnesia.utils.validation import as_list
from amnesia.modules.content_type import ContentType
from amnesia.modules.content.validation import ContentSchema
from amnesia.modules.content_type.validation import ContentTypeSchema


class FolderOrder(Schema):

    key = String(required=True)
    direction = String(required=True, validate=OneOf(('asc', 'desc')))
    nulls = String(required=True, validate=OneOf(('first', 'last')))


class FolderSchema(ContentSchema):
    ''' Schema for the Folder model '''

    content_id = Integer(dump_only=True)
    index_content_id = Integer(missing=None)
    polymorphic_loading = Boolean(missing=False)

    polymorphic_children = Nested(ContentTypeSchema, dump_only=True, many=True)
    polymorphic_children_ids = List(Integer, load_only=True)

    default_order = Nested(FolderOrder, many=True, default=[], missing=[])
    default_limit = Integer(missing=10, default=10,
                            validate=OneOf((10, 50, 100, 500)))

    ########
    # LOAD #
    ########

    @pre_load
    def pre_load_adapt_polymorphic(self, data, **kwargs):
        try:
            data['polymorphic_children_ids'] = as_list(
                data['polymorphic_children_ids']
            )
        except KeyError:
            data['polymorphic_children_ids'] = []

        try:
            data['default_order'] = json.loads(data['default_order'])
        except (ValueError, TypeError):
            del data['default_order']
        except KeyError:
            data['default_order'] = []

        return data

    @post_load
    def post_load_adapt_polymorphic(self, data, **kwargs):
        if data.get('polymorphic_loading', None):
            pc = data.get('polymorphic_children_ids', [])
            if pc:
                stmt_pc = sql.select(ContentType).filter(
                    ContentType.id.in_(pc)
                )
                pc = self.dbsession.execute(stmt_pc).scalars().all()
            data['polymorphic_children'] = pc
        else:
            data['polymorphic_children'] = []

        return data
