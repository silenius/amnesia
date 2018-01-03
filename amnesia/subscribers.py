# -*- coding: utf-8 -*-

import logging

from pyramid.events import BeforeRender
from pyramid.events import subscriber

from amnesia import helpers

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@subscriber(BeforeRender)
def add_renderers_global(event):
    event['h'] = helpers
    widgets = event['request'].registry['widgets']
    event['widgets'] = widgets
