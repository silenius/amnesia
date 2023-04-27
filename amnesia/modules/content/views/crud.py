import logging

from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.modules.content import Entity
from amnesia.views import BaseView

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    config.scan(__name__)


@view_defaults(context=Entity)
class ContentCRUD(BaseView):

    @property
    def entity(self):
        return self.context.entity

    @property
    def session(self):
        return self.request.session

    def schema(self, factory, *, exclude=None, extra_context=None):
        perms = {
            ('acls', 'manage_acl'),
            ('default_order', 'manage_folder_order')
        }

        fields = {
            field for (field, permission) in perms
            if not self.request.has_permission(permission)
        }

        if exclude:
            fields |= exclude

        context = {
            'request': self.request, 
            'entity': self.context.entity
        }

        if extra_context:
            context |= extra_context


        return factory(
            context=context,
            exclude=fields
        )

        
    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()
