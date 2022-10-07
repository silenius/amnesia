from pyramid.events import subscriber

from .events import LoginFailureEvent
from .events import LoginSuccessEvent

from amnesia.modules.account import AccountAuditLogin


def includeme(config):
    config.scan(__name__)


@subscriber(LoginFailureEvent)
@subscriber(LoginSuccessEvent)
def add_login_entry(event):
    entry = AccountAuditLogin(
        event.account, event.request.client_addr, event.success
    )

    event.request.dbsession.add(entry)
