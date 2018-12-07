import falcon
import yaml
from composition_root import FalconContainer
from infrastructure.framework.falcon.controllers import InfoController


def error_serializer(req, resp, exception):
    representation = None
    preferred = req.client_prefers(('application/x-yaml',
                                    'application/json'))
    if preferred is not None:
        if preferred == 'application/json':
            representation = exception.to_json()
        else:
            representation = yaml.dump(exception.to_dict(),
                                       encoding=None)
        resp.body = representation
        resp.content_type = preferred
    resp.append_header('Vary', 'Accept')


app = falcon.API()
app.set_error_serializer(error_serializer)
app.add_route('/', FalconContainer.info_controller_factory())
app.add_route('/items', FalconContainer.items_controller_factory())