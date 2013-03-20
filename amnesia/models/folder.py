# -*- coding: utf-8 -*-

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

    @orm.validates('polymorphic_children', include_removes=True)
    def validate_polymorphic_children(self, key, value, is_remove):
        """ This validator maintains the consistency between default_order and
        polymorphic children.

        When an entry is removed from polymorphic_children (so, the underlying
        table will _not_ be joined anymore in the orm.with_polymorphic()),
        ensure that no default ordering has been specified on a column of that
        table in default_order
        """

        if is_remove and self.default_order:
            to_remove = lambda x: x['polymorphic_identity'] != value.id
            self.default_order = filter(to_remove, self.default_order)

        return value

    @orm.validates('default_order')
    def validate_default_order(self, key, value):
        """ Ensure consistency of the Folder.default_order column.

        This function checks the value that will be serialized as default_order.
        It must be a list of dict, each dict containing the following keys:

        column : the column on which we plan to ORDER BY.
        polymorphic_identity : used to retrieve the entity.
        weight : position of the column in the ORDER BY clause.
        order : 'asc' or 'desc'

        Example:

        [{'column': 'starts', 'polymorphic_identity': 5, 'weight': 1,
          'order': 'desc'},

         {'column': 'weight', 'polymorphic_identity': None, 'weight': 2,
          'order': 'asc'},

         {'column': 'last_update', 'polymorphic_identity': None, 'weight': 3,
          'order': 'asc'}]

        Note: a polymorphic_identity of None correspond to the base-most Mapper in
        the inheritance chain (Content in this case)
        """

        pl = self.polymorphic_loading

        if pl is False or not value:
            return None
        elif pl is True:
            keys = frozenset(('column', 'polymorphic_identity', 'weight', 'order'))
            base_mapper = orm.object_mapper(self).base_mapper
            pm = base_mapper.polymorphic_map

            # Identities that are supposed to be joined with orm.with_polymorphic
            valid_identities = {i.id for i in self.polymorphic_children}
            valid_orders = []

            for order in value:
                # All keys must be present
                if frozenset(order) == keys:
                    identity = order['polymorphic_identity']

                    # If polymorphic loading is enabled, check that the
                    # 'polymorphic_identity' is valid (which means that the
                    # identity is present in polymorphic_children), that the
                    # column exists, and that we're allowed to ORDER BY on that
                    # column.
                    if identity in valid_identities or identity is None:
                        cls = pm.get(identity, base_mapper).class_
                        col = getattr(cls, order['column'], None)

                        if col is not None and col in cls.__order__:
                            valid_orders.append(order)

            return valid_orders if valid_orders else None
