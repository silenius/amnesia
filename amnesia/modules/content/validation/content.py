import json
import logging

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_load
from marshmallow import pre_load
from marshmallow import pre_dump
from marshmallow import post_dump
from marshmallow import ValidationError

from marshmallow.fields import Boolean
from marshmallow.fields import DateTime
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.fields import Nested
from marshmallow.fields import List

from marshmallow.validate import Range
from marshmallow.validate import OneOf

from sqlalchemy import inspect
from sqlalchemy import sql

from amnesia.utils.validation import PyramidContextMixin
from amnesia.utils.validation import as_list
from amnesia.utils.validation.fields import JSON
from amnesia.modules.folder import Folder
from amnesia.modules.content_type.validation import ContentTypeSchema
from amnesia.modules.account.validation import AccountSchema
from amnesia.modules.account.validation import ACLSchema
from amnesia.modules.state.validation import StateSchema
from amnesia.modules.account import ContentACL

log = logging.getLogger(__name__)


class ContentSchema(Schema, PyramidContextMixin):
    """Base class for Content validation"""

    id = Integer(dump_only=True)
    added = DateTime(dump_only=True)
    updated = DateTime(dump_only=True)
    last_update = DateTime(dump_only=True)
    title = String()
    description = String(missing=None)
    effective = DateTime(missing=None)
    expiration = DateTime(missing=None)
    exclude_nav = Boolean(missing=False)
    is_fts = Boolean(missing=False)
    weight = Integer(dump_only=True)
    content_type_id = Integer(dump_only=True)
    type = Nested(ContentTypeSchema, dump_only=True)
    owner = Nested(AccountSchema, dump_only=True)
    container_id = Integer(dump_only=True)
    state = Nested(StateSchema, dump_only=True)
    parent = Nested('ContentSchema', exclude=('parent', ), dump_only=True)
    inherits_parent_acl = Boolean()
    on_success = Integer(default=201, missing=201, validate=OneOf((201, 303)))

    acls = Nested('ContentACLSchema', exclude=('content', ), 
                  dump_only=True, many=True)

    inherits_parent_acl = Boolean(missing=True)

    props = JSON(missing=None, default=None)
    #all_props = JSON(missing=None, default=None)

    class Meta:
        unknown = EXCLUDE

    ########
    # DUMP #
    ########

    @post_dump
    def post_dump_all_props(self, data, **kwargs):
        entity = self.context.get('entity')
        
        if entity:
            insp = inspect(entity)
        
            if 'all_props' in insp.attrs and not 'all_props' in insp.unloaded:
                data['all_props'] = entity.all_props

        return data

    ########
    # LOAD #
    ########

    @pre_load
    def pre_load_process(self, data, **kwargs):
        _data = {k: None if v == '' else v for k, v in data.items()}

        # ACLS
        if 'acls' in self.exclude:
            del(_data['acls'])
        elif 'acls' in _data:
            _data['acls'] = json.loads(_data['acls'])

        return _data

    @post_load
    def post_load_process(self, item, **kwargs):
        if 'container_id' in item:
            item['parent'] = self.dbsession.get(Folder, item.pop('container_id'))

        if 'acls' in item:
            item['acls'] = [
                ContentACL(allow=x['allow'], role_id=x['role_id'], 
                           permission_id=x['permission_id'], weight=weight)
                for weight, x in enumerate(reversed(item['acls']), 1)
            ]

        entity = self.context.get('entity')
        if not self.request.has_permission('manage_acl'):
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


class IdListSchema(Schema):
    ids = List(Integer(validate=Range(min=1)), required=True)

    @pre_load
    def ensure_list(self, data, **kwargs):
        try:
            data['ids'] = as_list(data['ids'])
        except KeyError:
            data['ids'] = []

        return data


class ContentACLSchema(ACLSchema):
    content = Nested(ContentSchema, dump_only=True)

    class Meta:
        unknown = EXCLUDE
