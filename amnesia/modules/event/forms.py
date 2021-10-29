from sqlalchemy import sql

from amnesia.modules.country import Country
from amnesia.modules.content.forms import ContentForm

class EventForm(ContentForm):

    template = 'amnesia:templates/event/_form.pt'

    def __init__(self, request, template=None):
        super().__init__(request, template)

    def render(self, data=None, errors=None, meta=None):
        if data is None:
            data = {}

        if 'countries' not in data:
            data['countries'] = self.dbsession.execute(
                sql.select(Country).order_by(Country.name)
            ).scalars().all()

        return super().render(data, errors)
