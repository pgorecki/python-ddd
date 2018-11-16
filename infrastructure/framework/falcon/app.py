import falcon
import json
from application.commands import AddItemCommand
from application.settings import APPLICATION_NAME 

# TODO: command_bus should be injected by DI
from application.command_bus import CommandBus
command_bus = CommandBus()

class Info(object):
    def on_get(self, req, res):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME
        }
        res.body = json.dumps(doc, ensure_ascii=False)
        res.status = falcon.HTTP_200

class ItemsController(object):
    def on_get(self, req, res):
        command = AddItemCommand(req.params, strict=False)
        command.validate()
        result = command_bus.execute(command)
        res.body = json.dumps(result, ensure_ascii=False)
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        pass

app = falcon.API()
app.add_route('/info', Info())
app.add_route('/items', ItemsController())


from domain.entities import AuctionItem
