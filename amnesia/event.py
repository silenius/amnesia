from pyramid.events import BeforeRender
from pyramid.events import subscriber
from pyramid.settings import asbool

from sqlalchemy import orm

from amnesia import widgets
from saexts import Serializer

from amnesia.utils.text import shorten
from amnesia.utils.text import fmt_datetime
from amnesia.utils.gravatar import gravatar
from amnesia.modules.event.utils import pretty_date
from amnesia.modules.content import Content


def includeme(config):
    config.scan(__name__)


def dump_obj(obj, format, **kwargs):
    return getattr(Serializer(obj), format)(**kwargs)

def polymorphic_hierarchy(cls=Content):
    return list(orm.class_mapper(cls).base_mapper.polymorphic_iterator())


@subscriber(BeforeRender)
def globals_factory(event):
    event['h'] = {
        'shorten': shorten,
        'fmt_datetime': fmt_datetime,
        'event_date': pretty_date,
        'gravatar': gravatar,
        'polymorphic_hierarchy': polymorphic_hierarchy,
        'asbool': asbool,
    }

    event['widgets'] = widgets
    event['dump_obj'] = dump_obj
