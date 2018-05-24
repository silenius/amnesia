# -*- coding: utf-8 -*-

from amnesia.modules.content import Content


def includeme(config):
    config.set_translatable_attrs(Content, ('title', 'description'))
