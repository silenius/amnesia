# -*- coding: utf-8 -*-

import logging

from pyramid.events import BeforeRender
from pyramid.events import subscriber

from amnesia import helpers
from amnesia import widgets

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@subscriber(BeforeRender)
def add_renderes_global(event):
    event['h'] = helpers
    event['widgets'] = widgets
