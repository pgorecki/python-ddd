import falcon
import json
from application.commands import AddItemCommand
from application.settings import APPLICATION_NAME


class InfoController(object):
    def on_get(self, req, res):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME,
        }
        res.body = json.dumps(doc, ensure_ascii=False)
        res.status = falcon.HTTP_200


class ItemsController(object):
    def __init__(self, command_bus, items_service):
        self._command_bus = command_bus
        self._items_service = items_service

    def on_get(self, req, res):
        result = self._items_service.get_all()
        res.body = result
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        command = AddItemCommand(req.media, strict=False)
        if not command.is_valid():
            res.status = falcon.HTTP_400
            # TODO: Add error details
            return
        # try:
        result = self._command_bus.execute(command)
        res.body = result.to_json()
        res.status = falcon.HTTP_200
        # except:
        #     # TODO: Handle app exception
        #     pass

