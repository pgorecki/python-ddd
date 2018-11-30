import falcon
import json
from application.commands import AddItemCommand
from application.settings import APPLICATION_NAME
from application.queries import GetItemsQuery
from application.response import json_response


class InfoController(object):
    def on_get(self, req, res):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME,
        }
        res.body = json_response(doc)
        res.status = falcon.HTTP_200


class ItemsController(object):
    def __init__(self, command_bus, query_bus):
        self._command_bus = command_bus
        self._query_bus = query_bus

    def on_get(self, req, res):
        query = GetItemsQuery()
        if not query.is_valid():
            res.status = falcon.HTTP_400
            # TODO: Add error details
            return

        result = self._query_bus.execute(query)
        res.body = json_response(result)
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        command = AddItemCommand(req.media, strict=False)
        if not command.is_valid():
            res.status = falcon.HTTP_400
            # TODO: Add error details
            return
        # try:
        result = self._command_bus.execute(command)
        res.body = json_response(result)
        res.status = falcon.HTTP_200
        # TODO: change to ActionResult (metadata - status, data, etc.)
        # except:
        #     # TODO: Handle app exception
        #     pass
