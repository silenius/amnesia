import json

from marshmallow import ValidationError
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder import FolderBrowser
from amnesia.modules.folder.services import get_lineage
from amnesia.modules.folder.services import get_children_containers
from amnesia.modules.file import File
from amnesia.modules.document import Document
from amnesia.modules.file.validation.file import FileSchema
from amnesia.modules.folder.validation import FolderBrowserSchema
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.document.validation import DocumentSchema
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=FolderEntity)
class FolderBrowserView(BaseView):

    @view_config(
        request_method='GET',
        renderer='json',
        name='browse',
        accept='application/json'
    )
    def browse_json(self):
        params = self.request.GET.mixed()
        schema = FolderBrowserSchema(context={
            'request': self.request,
            'folder': self.context.entity
        })

        factories = {
            File: FileSchema,
            Document: DocumentSchema
        }

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        browser = FolderBrowser(self.request, self.context.entity)
        result = browser.query(**data)

        from amnesia.modules.content.validation import ContentSchema

        return [
            factories.get(o.__class__, ContentSchema)().dump(o)
            for o in result.query.all()
        ]

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
        self.request.response.text = json.dumps(result, cls=Encoder)

        return self.request.response
