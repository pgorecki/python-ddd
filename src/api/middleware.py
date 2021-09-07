from os import umask


import uuid
from starlette_context.plugins import Plugin


class RequestContextPlugin(Plugin):
    key = "request_context"

    def __init__(self, container) -> None:
        super().__init__()
        self.container = container

    async def process_request(self, request):
        """When processing a request, we set up a new request context"""
        context = self.container.request_context()
        context._correlation_id.set(uuid.uuid4())
