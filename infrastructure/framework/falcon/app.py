import falcon
import json
from application.application import APPLICATION_NAME 

class Info(object):

    def on_get(self, req, resp):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME
        }
        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = falcon.HTTP_200

app = falcon.API()
app.add_route('/info', Info())
