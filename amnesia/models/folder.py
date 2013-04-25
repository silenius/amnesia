# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import itemgetter

from sqlalchemy import orm

from amnesia import db
from amnesia.models import content


class FolderQuery(content.ContentQuery):

    def ___init__(self, *args, **kwargs):
        super(FolderQuery, self).__init__(*args, **kwargs)


class Folder(content.Content):

    query = db.Session.query_property(FolderQuery)

    def __init__(self, **kwargs):
        super(Folder, self).__init__(**kwargs)

    def feed(self, **kwargs):
        # Those columns must be loaded at first.
        for c in ('polymorphic_loading', 'polymorphic_children'):
            if c in kwargs:
                setattr(self, c, kwargs.pop(c))
        super(Folder, self).feed(**kwargs)

    @property
    def polymorphic_config(self):
        """ Returns a namedtuple with the following:

        pm : a filtered polymorphic map (if polymorphic_children is found) or an
        empty dict (if polymorphic_loading if False) or the base mapper
        polymorphic map (if polymorphic loading is True).

        base : the base-most Mapper in the inheritance chain.

        cls : classes which are found in the polymorphic map

        orders : orders for those classes """

        base_mapper = orm.object_mapper(self).base_mapper

        # A "filtered" polymorphic_map which contain only mappers depending of
        # the configuration of polymorphic_loading/polymorphic_children.
        if self.polymorphic_loading:
            pm = base_mapper.polymorphic_map
            if self.polymorphic_children:
                # Remove mappers from the original polymorphic_map for which
                # identity is not found in polymorphic_children.
                identities = {i.id for i in self.polymorphic_children}
                pm = {k: v for (k, v) in pm.iteritems() if k in identities}
        else:
            # If no polymorphic loading, then _no_ mappers will be joined.
            pm = {}

        # Classes that should be automatically joined in the polymorphic
        # loading. It can be directly used with orm.with_polymorphic()
        cls = [m.class_ for m in pm.itervalues()]

        # Fetch available orders. Note: we've to include the base-most Mapper
        # class as it doesn't appear in the polymorphic map.
        orders = {order for entity in cls + [base_mapper.class_]\
                        for order in entity._SORTS_}

        cfg = namedtuple('PolymorphicConfig', ('pm', 'base', 'cls', 'orders'))

        return cfg(pm, base_mapper, cls, orders)

    ##############
    # VALIDATORS #
    ##############

    @orm.validates('polymorphic_children', include_removes=True)
    def validate_polymorphic_children(self, key, value, is_remove):
        """ This validator maintains the consistency between default_order and
        polymorphic_children.

        When an entry is removed from polymorphic_children (so, the underlying
        table will _not_ be joined anymore in the orm.with_polymorphic()),
        ensure that no default ordering has been specified on a column of that
        table in default_order, otherwise we could end up with a missing table
        in the final FROM clause """

        if is_remove and self.default_order:
            self.default_order = filter(
                lambda x: x['polymorphic_identity'] != value.id,
                self.default_order)

        return value

    @orm.validates('default_order')
    def validate_default_order(self, key, value):
        """ Ensure consistency of the Folder.default_order column.

        This function checks the value that will be serialized in
        the default_order column. """

        orders = [order for order in value if\
                  self.to_polymorphic_order(order) is not None]

        # Stores the list sorted on the 'weight' column
        orders.sort(key=itemgetter('weight'))

        return orders if orders else None

    def to_polymorphic_order(self, order):
        """ Check a polymorphic order.

        The order must be a dict with the following keys:

        'key' : the column on which we plan to ORDER BY.

        'polymorphic_identity' : used to retrieve the entity. Match all the
         polymorphic_identity of the orm.mapper() in the models/__init__.py
         file.

        'weight' : position of the column in the ORDER BY clause.

        'order' : 'asc' or 'desc' (sort direction)

        Examples:
        =========

        {'key': 'starts', 'polymorphic_identity': 5, 'weight': 1,
         'order': 'desc'}

        {'key': 'weight', 'polymorphic_identity': None, 'weight': 2,
         'order': 'asc'}

        {'key': 'last_update', 'polymorphic_identity': None, 'weight': 3,
         'order': 'asc'}

        Note:
        =====

        A polymorphic_identity of None correspond to the base-most Mapper in
        the inheritance chain (Content in this case) """

        keys = frozenset(('key', 'polymorphic_identity', 'weight', 'order'))

        if frozenset(order) == keys:
            pl_cfg = self.polymorphic_config
            identity = order['polymorphic_identity']
            if identity in pl_cfg.pm or identity is None:
                cls = pl_cfg.pm.get(identity, pl_cfg.base).class_
                col = getattr(cls, order['key'], None)

                if col is not None and col in cls._SORTS_:
                    return col.desc() if order['order'] == 'desc' else col

        return None
