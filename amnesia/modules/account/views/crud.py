import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Account
from amnesia.modules.account import AccountEntity
from amnesia.modules.account import AuthResource
from amnesia.modules.account.validation import AccountSchema


log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_defaults(
    context=AccountEntity,
    permission='manage_accounts',
    name=''
)
class AccountCRUD(BaseView):

    #########
    # PATCH #
    #########

    @view_config(
        request_method='PATCH',
        renderer='json',
    )
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(AccountSchema)

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        if 'enabled' in data:
            self.context.entity.enabled = data['enabled']

        return schema.dump(self.context.entity)

    ##########
    # DELETE #
    ##########

    @view_config(
        request_method='DELETE',
    )
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()


@view_defaults(
    context=AuthResource
)
class AccountManager(BaseView):

    @view_config(
        request_method='GET',
        renderer='json',
        name='me'
    )
    def get(self):
        user = self.request.user
        
        if user:
            schema = self.schema(AccountSchema)
            return schema.dump(user)

        return None
