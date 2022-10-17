class RequestMixin:

    @property
    def dbsession(self):
        return self.request.dbsession

    @property
    def registry(self):
        return self.request.registry

    @property
    def notify(self):
        return self.registry.notify

    @property
    def settings(self):
        return self.registry.settings
