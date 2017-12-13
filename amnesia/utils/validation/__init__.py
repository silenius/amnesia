# -*- coding: utf-8 -*-

from .helpers import TRUE
from .helpers import FALSE
from .helpers import is_true
from .helpers import is_false
from .helpers import as_list


class PyramidContextMixin:

    @property
    def request(self):
        return self.context['request']

    @property
    def dbsession(self):
        return self.request.dbsession

    @property
    def registry(self):
        return self.request.registry

