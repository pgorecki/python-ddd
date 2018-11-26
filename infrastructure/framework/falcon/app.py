import falcon
from composition_root import FalconContainer
from infrastructure.framework.falcon.controllers import InfoController

app = falcon.API()
app.add_route('/', FalconContainer.info_controller_factory())
app.add_route('/items', FalconContainer.items_controller_factory())