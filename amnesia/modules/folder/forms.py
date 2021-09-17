from sqlalchemy import sql

from amnesia.modules.content.forms import ContentForm

class FolderForm(ContentForm):

    template = 'amnesia:templates/folder/_form.pt'

    def __init__(self, request, template=None):
        super().__init__(request, template)

    def render(self, data=None, errors=None):
        if data is None:
            data = {}

        if 'polymorphic_children_ids' not in data:
            pc_ids = [i['id'] for i in data.get('polymorphic_children', ())]
            data['polymorphic_children_ids'] = pc_ids

        if 'default_order' not in data:
            data['default_order'] = []

        return super().render(data, errors)
