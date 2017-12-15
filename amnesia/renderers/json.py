# -*- coding: utf-8 -*-

import datetime

from pyramid.renderers import JSON


def datetime_adapter(obj, request):
    return obj.isoformat()


def includeme(config):
    json_renderer = JSON(indent=4)

    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    json_renderer.add_adapter(datetime.date, datetime_adapter)

    config.add_renderer('json', json_renderer)
