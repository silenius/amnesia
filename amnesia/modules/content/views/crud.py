# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.renderers import render_to_response

from amnesia.modules.content import Entity
from amnesia.modules.account import Permission
from amnesia.modules.account import Role
from amnesia.modules.account.security import get_parent_acl
from amnesia.modules.tag import Tag
from amnesia.utils.forms import render_form
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
    def dbsession(self):
        return self.request.dbsession

    @property
    def session(self):
        return self.request.session

    def edit_form(self, form_data, errors=None, view=None):
        if errors is None:
            errors = {}

        if view:
            action = self.request.resource_path(self.context, view)
        else:
            action = self.request.resource_path(self.context)

        return {
            'form': self.form(form_data, errors),
            'form_action': action
        }

    def form(self, data=None, errors=None):
        if data is None:
            data = {}

        if 'all_tags' not in data:
            q_tag = self.dbsession.query(Tag)
            data['all_tags'] = q_tag.order_by(Tag.name).all()

        if 'props' not in data:
            data['props'] = {}

        if self.request.has_permission('manage_acl'):
            if 'permissions' not in data:
                data['permissions'] = self.dbsession.query(Permission).order_by(
                    Permission.name)

            if 'parent_acl' not in data:
                data['parent_acl'] = get_parent_acl(self.context)

            if 'roles' not in data:
                data['roles'] = self.dbsession.query(Role).order_by(Role.virtual.desc())

        if 'is_fts' not in data:
            data['is_fts'] = True

        data['csrf_token'] = self.session.get_csrf_token()

        return render_form(self.form_tmpl, self.request, data, errors=errors)

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(request_method='GET', permission='read', accept='text/html')
    def read(self):
        context = {
            'content': self.entity
        }

        try:
            # Is a default template registered for this entity ?
            template = self.entity.props['template_show']
            return render_to_response(template, context, request=self.request)
        except (TypeError, KeyError):
            # No default template is defined in props['template_show']
            # The caller should provide a renderer='mypacakge:sometemplate.pt'
            return context
        except (FileNotFoundError, ValueError):
            # A default template has been provided, but is not found
            raise HTTPNotFound()

    #########################################################################
    # DELETE                                                                #
    #########################################################################

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()
