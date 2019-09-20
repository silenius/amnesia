# -*- coding: utf-8 -*-

import json

from sqlalchemy import orm

from marshmallow import Schema
from marshmallow import pre_load
from marshmallow import post_load
from marshmallow.fields import Nested
from marshmallow.fields import List
from marshmallow.fields import Integer
from marshmallow.fields import Boolean

from amnesia.utils.validation import as_list
from amnesia.modules.folder.validation import FolderOrder
from amnesia.modules.content import Content


class PolymorphicOrderSelectionSchema(Schema):

    selected = Nested(FolderOrder, many=True)
    pc = List(Integer)
    pl = Boolean()

    # LOAD

    @pre_load
    def pre_load_adapt_polymorphic(self, data, **kwargs):
        data['pc'] = as_list(data.get('pc', ()))

        try:
            data['selected'] = json.loads(data['selected'])
        except (ValueError, TypeError, KeyError):
            data['selected'] = []

        return data

    @post_load
    def post_load_adapt_polymorphic(self, data, **kwargs):
        entities = []
        pm = orm.class_mapper(Content).polymorphic_map

        # Polymorphic loading
        if data['pl']:
            # Polymorphic children
            entities = data['pc']

            if entities:
                entities = [pm[i].class_ for i in entities]
            else:
                entities = [pm[i].class_ for i in pm]

        data['entities'] = entities

        return data
