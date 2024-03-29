from .model import Account
from .model import Role
from .model import Permission
from .model import AccountRole
from .model import ACL
from .model import GlobalACL
from .model import ContentACL
from .model import ACLResource

from .resources import AuthResource
from .resources import DatabaseAuthResource
from .resources import AccountEntity
from .resources import ACLEntity
from .resources import ContentACLEntity
from .resources import RoleResource
from .resources import RoleEntity
from .resources import RoleMember
from .resources import RoleMemberEntity


def _get_user(request):
    return request.identity

def includeme(config):
    config.add_request_method(_get_user, 'user', reify=True)

    config.include('.mapper')
    config.include('.views')
