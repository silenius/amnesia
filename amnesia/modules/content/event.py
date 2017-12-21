# -*- coding: utf-8 -*-

class ContentCreatedEvent:

    def __init__(self, request, content):
        self.request = request
        self.content = content


class ContentDeletedEvent:

    def __init__(self, request, content):
        self.request = request
        self.content = content

