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
            template = self.entity.props['template_show']
        except (TypeError, KeyError):
            template = 'amnesia:templates/{}/show.pt'.format(
                self.entity.type.name)

        try:
            return render_to_response(template, context, request=self.request)
        except (FileNotFoundError, ValueError):
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
        request.tm.commit()
        return {'deleted': True}
    except DatabaseError:
        request.tm.abort()
        return {'deleted': False}
