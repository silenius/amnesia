from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.content.validation import IdListSchema
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder.exc import PasteError
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=FolderEntity)
class paste(BaseView):

    @view_config(
        request_method='POST', 
        name='paste',
        renderer='json',
        permission='paste'
    )
    def paste(self):
        schema = self.schema(IdListSchema)
        form_data = self.request.POST.mixed()

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        pasted = self.context.paste(data['ids'])
        
        return {'pasted': pasted}
