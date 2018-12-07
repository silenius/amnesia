# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.renderers import render_to_response

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Content
from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.content.validation import IdListSchema
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

    def form(self, data=None, errors=None):
        if data is None:
            data = {}

        if 'all_tags' not in data:
            q_tag = self.dbsession.query(Tag)
            data['all_tags'] = q_tag.order_by(Tag.name).all()

        if 'props' not in data:
            data['props'] = {}

        if 'is_fts' not in data:
            data['is_fts'] = True

        data['csrf_token'] = self.request.session.get_csrf_token()

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
        return self.context.delete()


@view_config(request_method='POST', context=EntityManager, name='delete',
             renderer='json', permission='delete')
def delete(context, request):
    try:
        result = IdListSchema().load(request.POST.mixed())
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)

    dbsession = request.dbsession

    ids = result['oid']
    query = dbsession.query(Content).filter(Content.id.in_(ids))

    for entity in query:
        dbsession.delete(entity)

    try:
        dbsession.flush()
        return {'deleted': True}
    except DatabaseError:
        return {'deleted': False}
