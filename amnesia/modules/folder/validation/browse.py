import copy

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import INCLUDE
from marshmallow import post_load
from marshmallow import pre_load

from marshmallow.fields import String
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Field
from marshmallow.fields import Nested
from marshmallow.fields import Boolean

from marshmallow.validate import OneOf
from marshmallow.validate import Range

from amnesia.utils.validation import PyramidContextMixin
from amnesia.utils.validation import as_list


MAX_SORT = 10


class SortListField(Field, PyramidContextMixin):

    def __init__(self, nested_field, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested_field = nested_field

    def _deserialize(self, value, attr, data, **kwargs):
        ret = []

        for i in range(0, MAX_SORT):

            sort_key = '__s{:d}'.format(i)
            s = data.get(sort_key, '').strip()

            if not s:
                break

            if s not in self.registry.settings['amnesia:orders']:
                continue

            nested = {'key': s}

            for opt in ('direction', 'nulls'):
                k = '{0}{1}'.format(sort_key, opt)
                if k in data:
                    nested[opt] = data[k].strip()

            ret.append(self.nested_field.deserialize(nested))

        return ret


class SortSchema(Schema):

    key = String(required=True)
    direction = String(required=True, validate=OneOf(('asc', 'desc')))
    nulls = String(required=True, validate=OneOf(('first', 'last')))


class FolderBrowserSchema(Schema, PyramidContextMixin):

    limit = Integer(validate=OneOf((10, 50, 100, 500)), missing=None)
    offset = Integer(validate=Range(min=0), missing=0)
    sort_by = SortListField(Nested(SortSchema), missing=[])
    deferred = List(String(), missing=())
    undeferred = List(String(), missing=())
    sort_folder_first = Boolean(missing=True)
    filter_types = List(String())
    filter_mimes = List(String())
    only_published = Boolean(missing=True)

    class Meta:
        unknown = INCLUDE

    @pre_load
    def ensure_list(self, data, **kwargs):
        for k in ('filter_types', 'filter_mimes'):
            try:
                data[k] = as_list(data[k])
            except KeyError:
                data[k] = []

        return data

    @post_load
    def make_sort(self, data, **kwargs):
        orders = self.registry.settings['amnesia:orders']
        sort_by = []

        # XXX: this should be done in the "SQLAlchemy way"
        def _convert(sort):
            key = sort['key']

            if key not in orders:
                return None

            copy_sort = copy.copy(orders[key])

            if 'direction' in sort:
                copy_sort.direction = sort['direction']

            if 'nulls' in sort:
                copy_sort.nulls = sort['nulls']

            return copy_sort

        for s in data['sort_by']:
            _sort = _convert(s)
            if _sort:
                sort_by.append(_sort)

        if not sort_by:
            entity = self.request.context.entity
            if entity and entity.default_order:
                for s in entity.default_order:
                    _sort = _convert(s)
                    if _sort:
                        sort_by.append(_sort)

        data['sort_by'] = sort_by

        return data
