# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import itemgetter

from sqlalchemy import orm

from ..content import Content


class Folder(Content):

    default_order_keys = frozenset(('key', 'order', 'nulls'))

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

        cls : classes which are found in the polymorphic map """

        base_mapper = orm.object_mapper(self).base_mapper

        # If polymorphic loading is enabled pm will contain the mappers that
        # should be joined, if not then "pm" will be empty.
        pm = base_mapper.polymorphic_map if self.polymorphic_loading else {}

        if pm and self.polymorphic_children:
            # Remove mappers from the original polymorphic_map for which
            # identity is not found in polymorphic_children.
            identities = {i.id for i in self.polymorphic_children}
            pm = {k: v for (k, v) in pm.items() if k in identities}

        # Classes that should be automatically joined in the polymorphic
        # loading. It can be directly used with orm.with_polymorphic()
        cls = [m.class_ for m in pm.values()]

        cfg = namedtuple('PolymorphicConfig', ('pm', 'base_mapper', 'cls'))

        return cfg(pm, base_mapper, cls)

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
        in the final FROM clause

        Parameters
        ----------
        value : ContentType

        """

        if is_remove and self.default_order:
            # FIXME
            from amnesia.models import orders
            self.default_order = [x for x in self.default_order
                                  if orders[x['key']].identity != value.id]

        return value

    @orm.validates('default_order')
    def validate_default_order(self, key, value):
        """ Ensure consistency of the Folder.default_order column.

        This function checks the value that will be serialized in
        the default_order column. """

        orders = [order for order in value if\
                  frozenset(order) == self.default_order_keys]

        return orders if orders else None
