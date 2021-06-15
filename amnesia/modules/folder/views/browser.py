import json

from random import choice

from marshmallow import ValidationError

from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPBadRequest

from sqlalchemy import sql

from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder import FolderBrowser
from amnesia.modules.folder.validation import FolderBrowserSchema
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.folder.services import get_lineage
from amnesia.modules.folder.services import get_children_containers
from amnesia.modules.file import File
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=FolderEntity)
class FolderBrowserView(BaseView):

    @view_config(request_method='GET', renderer='json',
                 name='browse', accept='application/json')
    def browse_json(self):
        params = self.request.GET.mixed()
        schema = FolderBrowserSchema(context={
            'request': self.request,
            'folder': self.context.entity
        })

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        browser = FolderBrowser(self.context.entity, self.request.dbsession)
        result = browser.query(**data)
        return {
            'results': schema.dump(result.query.all(), many=True)
        }

    @view_config(request_method='GET', name='browse')
    def browse(self, **kwargs):
        params = self.request.GET.mixed()
        schema = FolderBrowserSchema(context={
            'request': self.request,
            'folder': self.context.entity
        })

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        browser = FolderBrowser(self.context.entity, self.request.dbsession)
        result = browser.query(**data)

        data.update(result._asdict())
        data.update(kwargs)
        data['content'] = self.context.entity
        data['options'] = ()

        response = render_to_response('amnesia:templates/folder/_browse.xml',
                                      data, request=self.request)
        response.content_type = 'application/xml'

        return response

    @view_config(request_method='GET', name='browse_events')
    def browse_events(self):
        container_id = self.request.registry.settings['default_event_pictures_container_id']
        random_pictures = self.request.dbsession.query(File).filter_by(
            container_id=container_id).order_by(sql.func.random()).limit(50).all()
        random_picture = lambda: choice(random_pictures)
        return self.browse(random_picture=random_picture)

    @view_config(request_method='GET', name='browse_news')
    def browse_news(self):
        container_id = self.request.registry.settings['default_news_pictures_container_id']
        random_pictures = self.request.dbsession.query(File).filter_by(
            container_id=container_id).order_by(sql.func.random()).limit(50).all()
        random_picture = lambda: choice(random_pictures)
        return self.browse(random_picture=random_picture)

    @view_config(request_method='GET', name='children',
                 accept='application/json')
    def children(self):
        schema = FolderSchema(only=('id', 'title'))
        depth = None

        class Encoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Folder):
                    return schema.dump(obj)
                return super().default(obj)

        result = get_children_containers(
            self.request.dbsession,
            self.context.entity.id,
            max_depth=depth
        ).as_tree()

        self.request.response.content_type = 'application/json'
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'
        self.request.response.text = json.dumps(result, cls=Encoder)

        return self.request.response

    @view_config(request_method='GET', name='lineage',
                 accept='application/json')
    def lineage(self):
        schema = FolderSchema(only=('id', 'title'))

        class Encoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Folder):
                    return schema.dump(obj)
                return super().default(obj)

        result = get_lineage(
            self.request.dbsession,
            self.context.entity.id
        )

        self.request.response.content_type = 'application/json'
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'
        self.request.response.text = json.dumps(result, cls=Encoder)

        return self.request.response
