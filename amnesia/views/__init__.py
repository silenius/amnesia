# -*- coding: utf-8 -*-


def includeme(config):
    config.include('.haproxy')
    config.include('.index')
    config.include('.contact')


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def dbsession(self):
        return self.request.dbsession
