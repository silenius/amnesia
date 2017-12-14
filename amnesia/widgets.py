# -*- coding: utf-8 -*-

# pylint: disable=E1101

from calendar import monthrange
from datetime import date
from itertools import groupby

from pyramid.renderers import render

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.utils import itermonths
from amnesia.utils import polymorphic_ids
from amnesia.modules.content import Content
from amnesia.modules.document import Document
from amnesia.modules.event import Event
from amnesia.modules.folder import Folder
from amnesia.modules.file import File
from amnesia.modules.content_type import ContentType

__all__ = ['Navigation', 'Tabs']


class Widget(object):

    name = None
    template = None

    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    def __str__(self):
        return render(self.template, {'widget': self}, request=self.request)


class Navigation(Widget):

    name = 'navigation'
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
        hierarchy = """ WITH RECURSIVE parents AS (
            SELECT c.*, 1 as level FROM content c WHERE c.id=:content_id
                UNION ALL
            SELECT c.*, level+1 FROM content c
                                JOIN parents p ON p.container_id=c.id
        ) SELECT * FROM parents ORDER BY level DESC """

        return self.dbsession.query(Content).from_statement(hierarchy).\
            params(content_id=self.content.id)


class Tabs(Widget):

    name = 'tabs'
    template = 'amnesia:templates/widgets/tabs.pt'

    def __init__(self, request, root_id=None, **kwargs):
        super().__init__(request)

        q = """ WITH RECURSIVE parents AS (
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
        ) SELECT * FROM parents ORDER BY container_id, level DESC, weight DESC """

        self.kwargs = kwargs
        if 'template' in kwargs:
            self.template = kwargs['template']

        self.tabs = self.dbsession.query(Content).from_statement(q).\
            params(container_id=root_id).all()

        self.root_id = root_id

        # Group tabs per container_id
        grp_by_container = groupby(self.tabs, lambda x: x.container_id)
        self.grouped_tabs = {i[0]: tuple(i[1]) for i in grp_by_container}


class RecentPosts(Widget):

    name = 'recent posts'
    template = 'amnesia:templates/widgets/{}.pt'

    def __init__(self, request, limit=5, tmpl='recent_posts'):
        super().__init__(request)
        self.template = self.template.format(tmpl)

        entity = orm.with_polymorphic(Content, [Document, Event])

        filters = sql.and_(
            entity.filter_published(),
            ContentType.name.in_(['document', 'event'])
        )

        posts = self.dbsession.query(entity).join(entity.type).options(
            orm.contains_eager(entity.type)
        ).filter(filters).order_by(entity.added.desc()).limit(limit)

        self.posts = posts.all()


class Archives(Widget):

    name = 'archives'
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


class Twitter(Widget):

    name = 'twitter timeline'
    template = 'amnesia:templates/widgets/twitter.pt'

    def __init__(self, request, embed):
        super().__init__(request)
        self.embed = embed


class BoxRow(Widget):

    name = 'box row'
    template = 'amnesia:templates/widgets/box_row.pt'

    def __init__(self, request, root_id):
        super().__init__(request)
        self.root_id = root_id
        self.folder = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(root_id)

        if self.folder:
            self.documents = self.dbsession.query(Document).filter(
                Document.filter_published(),
                Document.filter_container_id(root_id)
            ).order_by(Document.weight.desc()).all()
        else:
            self.documents = []


class Slider1(Widget):
    name = 'slider1'
    template = 'amnesia:templates/widgets/slider1.pt'

    def __init__(self, request, root_id):
        super().__init__(request)
        self.root_id = root_id
        self.folder = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(root_id)

        if self.folder:
            self.files = self.dbsession.query(File).filter(
                File.filter_published(),
                File.filter_container_id(root_id)
            ).order_by(File.weight.desc()).all()
        else:
            self.files = []


class Slider2(Widget):

    name = 'slider2'
    template = 'amnesia:templates/widgets/slider2.pt'

    def __init__(self, request, root_id):
        super().__init__(request)
        self.root_id = root_id
        self.folder = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(root_id)

        if self.folder:
            self.documents = self.dbsession.query(Document).filter(
                Document.filter_published(),
                Document.filter_container_id(root_id)
            ).order_by(sql.func.random()).all()
        else:
            self.documents = []
