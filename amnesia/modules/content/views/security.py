import logging

from pyramid.view import view_config

from amnesia.views import BaseView
from amnesia.modules.content import Entity
from amnesia.modules.account import ContentACL
from amnesia.modules.account.security import get_parent_acl
from amnesia.modules.account.validation import ACLSchema
from amnesia.modules.content.validation import ContentACLSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)

class ACLS(BaseView):

    @view_config(
        name='acls',
        context=Entity,
        renderer='json'
    )
    def acls(self):
        schema = self.schema(ContentACLSchema, exclude=('content.acls', ))
        return [
            schema.dump(acl) 
            if isinstance(acl, ContentACL) else ACLSchema().dump(acl)
            for acl in get_parent_acl(self.context)
        ]
