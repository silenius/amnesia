from sqlalchemy.ext.indexable import index_property


class pg_json_property(index_property):
    def __init__(self, attr_name, index, cast_type, default=None):
        super().__init__(attr_name, index, default=default)
        self.cast_type = cast_type

    def expr(self, model):
        expr = super().expr(model)
        return expr.astext.cast(self.cast_type)
