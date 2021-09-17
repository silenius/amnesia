from sqlalchemy import sql

from amnesia.modules.content.forms import ContentForm

class FileForm(ContentForm):

    template = 'amnesia:templates/file/_form.pt'

    def __init__(self, request, template=None):
        super().__init__(request, template)
