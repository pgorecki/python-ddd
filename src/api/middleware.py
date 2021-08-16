from starlette_context.plugins import Plugin


class DependencyInjecionPlugin(Plugin):
    key = "container"

    def __init__(self, container) -> None:
        super().__init__()
        self.container = container

    async def process_request(self, request):
        return self.container
