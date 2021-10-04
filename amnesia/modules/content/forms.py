from sqlalchemy import sql

from amnesia.modules.account import Permission
from amnesia.modules.account import Role
from amnesia.modules.account.security import get_parent_acl
from amnesia.modules.tag import Tag

from amnesia.utils.forms import render_form


class AllSections:

    def __contains__(self, item):
        return True


class ContentForm:

    template = 'amnesia:templates/content/_form.pt'

    def __init__(self, request, template=None):
        self.request = request

        if template is None:
            template = self.template

    @property
    def dbsession(self):
        return self.request.dbsession

    @property
    def session(self):
        return self.request.session

    @property
    def context(self):
        return self.request.context

    def render(self, data=None, errors=None, meta=None, **kwargs):
        if errors is None:
            errors = {}

        if data is None:
            data = {}

        if meta is None:
            meta = {}

        if 'sections' not in meta:
            meta['sections'] = AllSections()

        if 'all_tags' not in data:
            data['all_tags'] = self.dbsession.execute(
                sql.select(Tag).order_by(Tag.name)
            ).scalars().all()

        if 'on_success' not in data:
            data['on_success'] = 303

        if 'props' not in data:
            data['props'] = {}

        if self.request.has_permission('manage_acl'):
            if 'permissions' not in data:
                data['permissions'] = self.dbsession.execute(
                    sql.select(Permission).order_by(Permission.name)
                ).scalars().all()

            if 'parent_acl' not in data:
                data['parent_acl'] = get_parent_acl(self.context)

            if 'roles' not in data:
                data['roles'] = self.dbsession.execute(
                    sql.select(Role).order_by(Role.virtual.desc())
                ).scalars().all()

        if 'is_fts' not in data:
            data['is_fts'] = True

        data['csrf_token'] = self.session.get_csrf_token()
        data['meta'] = meta

        return render_form(self.template, self.request, data, errors=errors)
