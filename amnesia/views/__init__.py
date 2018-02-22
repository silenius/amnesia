# -*- coding: utf-8 -*-


def includeme(config):
    config.include('.haproxy')
    config.include('.index')
    config.include('.contact')
    config.include('.newsletter')


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
