from pyramid.events import subscriber
from pyramid.settings import asbool

from sqlalchemy import sql

from .events import LoginFailureEvent
from .events import LoginSuccessEvent
from .events import LoginAttemptEvent

from .exc import TooManyAuthenticationFailure

from . import AccountAuditLogin
from .utils.audit import get_count_failures
from .utils.audit import reset_failures


def includeme(config):
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@subscriber(LoginSuccessEvent)
def add_success_login_entry(event):
    settings = event.request.registry.settings

    log_success = asbool(settings.get('audit.account.log_success', True))

    if log_success:
        entry = AccountAuditLogin(
            event.account, event.request.client_addr, True
        )

        event.request.dbsession.add(entry)

    reset_failures = asbool(settings.get('audit.account.reset_failures_on_success', False))

    if reset_failures:
        reset_failures(event.account, event.request.client_addr)


@subscriber(LoginFailureEvent)
def add_failed_login_entry(event):
    settings = event.request.registry.settings

    log_failure = asbool(settings.get('audit.account.log_failure', True))

    if log_failure:
        entry = AccountAuditLogin(
            event.account, event.request.client_addr, False
        )

        event.request.dbsession.add(entry)


@subscriber(LoginAttemptEvent)
def login_attempt(event):
    request = event.request
    settings = request.registry.settings
    dbsession = request.dbsession
    ip = request.client_addr
    account = event.account

    failure_limit = int(settings.get('audit.account.failure_limit'))
    if failure_limit > 0:
        if get_count_failures(dbsession, account, ip=ip) >= failure_limit:
            raise TooManyAuthenticationFailure(account, ip)
