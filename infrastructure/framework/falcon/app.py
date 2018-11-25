import falcon
from composition_root import FalconContainer
from infrastructure.framework.falcon.controllers import InfoController

app = falcon.API()
app.add_route('/', FalconContainer.infoController())
app.add_route('/items', FalconContainer.itemsController())


foo = FalconContainer.foo
print(foo())
