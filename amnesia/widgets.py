# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from calendar import monthrange
from datetime import date
from itertools import groupby

from pyramid.renderers import render
from pyramid.settings import aslist

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.utils import itermonths
from amnesia.utils import polymorphic_ids
from amnesia.modules.content import Content
from amnesia.modules.document import Document
from amnesia.modules.event import Event
from amnesia.modules.content_type import ContentType
from amnesia.modules.language import Language

from amnesia.utils.widgets import widget_config

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    config.scan(__name__)


class Widget(object):

    template = None

    def __init__(self, request):
        self.request = request

    @property
    def dbsession(self):
        return self.request.dbsession

    @property
    def settings(self):
        return self.request.registry.settings

    def __str__(self):
        return render(self.template, {'widget': self}, request=self.request)


@widget_config('navigation')
class Navigation(Widget):

    template = 'amnesia:templates/widgets/navigation.pt'

    def __init__(self, request, content_or_id, action=None, after_text=[],
                 **kwargs):
        super().__init__(request)
        self.action = action
        self.after_text = after_text
        self.obj_dump = kwargs.get('obj_dump')

        if isinstance(content_or_id, (int, str)):
            self.content = self.dbsession.query(Content).get(content_or_id)
        else:
            self.content = content_or_id

    @property
    def parents(self):
        hierarchy = sql.text('''WITH RECURSIVE parents AS (
            SELECT c.*, 1 as level FROM content c WHERE c.id=:content_id
                UNION ALL
            SELECT c.*, level+1 FROM content c
                                JOIN parents p ON p.container_id=c.id
        )
        SELECT * FROM parents ORDER BY level DESC''')

        return self.dbsession.query(Content).from_statement(hierarchy).\
            params(content_id=self.content.id)


@widget_config('tabs')
class Tabs(Widget):

    template = 'amnesia:templates/widgets/tabs.pt'

    def __init__(self, request, root_id=None, **kwargs):
        super().__init__(request)

        stmt = sql.text('''
            WITH RECURSIVE parents AS (
                SELECT
                    c.*, 1 AS level
                FROM
                    folder f
                JOIN
                    content c ON c.id = f.content_id
                WHERE
                    c.exclude_nav = FALSE
                    AND c.container_id = :container_id
                UNION ALL
                SELECT
                    c.*, level+1
                FROM
                    content c
                JOIN
                    folder f ON c.id = f.content_id
                JOIN
                    parents p ON p.id = c.container_id
                WHERE
                    c.container_id IS NOT NULL
                    AND c.exclude_nav=FALSE
            )
            SELECT *
            FROM parents
            ORDER BY container_id, level DESC, weight DESC ''')

        self.kwargs = kwargs
        if 'template' in kwargs:
            self.template = kwargs['template']

        self.tabs = self.dbsession.query(Content).from_statement(stmt).\
            params(container_id=root_id).all()

        self.root_id = root_id

        # Group tabs per container_id:
        grp_by_container = groupby(self.tabs, lambda x: x.container_id)
        self.grouped_tabs = {i[0]: tuple(i[1]) for i in grp_by_container}


@widget_config('recent_posts')
class RecentPosts(Widget):

    template = 'amnesia:templates/widgets/{}.pt'

    def __init__(self, request, limit=5, tmpl='recent_posts'):
        super().__init__(request)
        self.template = self.template.format(tmpl)

        entity = orm.with_polymorphic(Content, [Document, Event])

        filters = sql.and_(
            entity.filter_published(),
            ContentType.name.in_(['document', 'event'])
        )

        posts = self.dbsession.query(entity).join(entity.type).\
            options(orm.contains_eager(entity.type)).filter(filters).\
            order_by(entity.added.desc()).limit(limit)

        self.posts = posts.all()


@widget_config('language_selector')
class LanguageSelector(Widget):

    template = 'amnesia:templates/widgets/language_selector.pt'

    def __init__(self, request):
        super().__init__(request)
        langs = aslist(self.settings.get('available_languages', ''))
        self.available_languages = self.dbsession.query(Language).filter(
            Language.id.in_(langs)).order_by(Language.name)

    def url(self, lang):
        try:
            (quote, root, lang, *_) = self.request.script_name.split('/', 3)
            return self.request.resource_url(self.request.root, '..', lang)
        except ValueError:
            return self.request.resource_url(self.request.root, lang)


@widget_config('archives')
class Archives(Widget):

    template = 'amnesia:templates/widgets/archives.pt'

    def __init__(self, request, starts=None, count=-6, types='*'):
        super().__init__(request)

        if starts is None:
            starts = date.today()

        ranges = list(itermonths(starts, count))
        if count < 0:
            ranges = list(reversed(ranges))

        range_end_day = monthrange(*ranges[-1])[1]

        range_start = date(*ranges[0], 1)
        range_end = date(*ranges[-1], range_end_day)

        entity = orm.with_polymorphic(Content, types)

        filters = sql.and_(
            entity.filter_published(),
            entity.added.between(range_start, range_end)
        )

        self.types_ids = polymorphic_ids(entity, types) if types != '*' else []

        if self.types_ids:
            filters.append(entity.content_type_id.in_(self.types_ids))

        col = sql.func.date_trunc('month', entity.added)

        archives = self.dbsession.query(
            sql.func.count().label('cpt'),
            col.label('ts')
        ).join(entity.type).filter(filters).group_by(col).order_by(col.desc())

        self.archives = archives.all()
