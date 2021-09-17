from amnesia.modules.content.forms import ContentForm

class DocumentForm(ContentForm):

    template = 'amnesia:templates/document/_form.pt'

    def __init__(self, request, template=None):
        super().__init__(request, template)
