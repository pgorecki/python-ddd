import falcon
import json
from application.commands import AddItemCommand
from application.settings import APPLICATION_NAME 
 

class InfoController(object):
    def on_get(self, req, res):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME
        }
        res.body = json.dumps(doc, ensure_ascii=False)
        res.status = falcon.HTTP_200


class ItemsController(object):
    def __init__(self, command_bus):
        self.command_bus = command_bus

    def on_get(self, req, res):
        command = AddItemCommand(req.params, strict=False)
        command.validate()
        result = self.command_bus.execute(command)
        res.body = json.dumps(result, ensure_ascii=False)
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        pass
