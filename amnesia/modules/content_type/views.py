import logging

from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.modules.content_type import ContentTypeResource
from amnesia.modules.content_type.validation import ContentTypeSchema
from amnesia.views import BaseView

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@view_defaults(
    context=ContentTypeResource,
    name=''
)
class ContentTypeCRUD(BaseView):

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json'
    )
    def get(self):
        schema = ContentTypeSchema(
            context={'request': self.request}
        )
                                   
        types = self.dbsession.execute(
                self.context.query()
        ).scalars().all()

        return schema.dump(types, many=True)
