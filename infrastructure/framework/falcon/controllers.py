import falcon

from application.commands import AddItemCommand
from application.queries import GetItemsQuery
from application.response import json_response
from application.settings import APPLICATION_NAME
from infrastructure.framework.falcon.authentication import authenticate
from infrastructure.framework.falcon.base import RouteController


class InfoController(RouteController):
    def on_get(self, req, res):
        doc = {
            'framework': 'Falcon {}'.format(falcon.__version__),
            'application': APPLICATION_NAME,
        }
        res.body = json_response(doc)
        res.status = falcon.HTTP_200


class ItemsController(RouteController):
    def on_get(self, req, res):
        query = GetItemsQuery()
        if not query.is_valid():
            res.status = falcon.HTTP_400
            # TODO: Add error details
            return

        result = self._query_bus.execute(query)
        res.body = json_response(result)
        res.status = falcon.HTTP_200

    @authenticate
    def on_post(self, req, res):
        command = AddItemCommand({
            **req.media,
            'seller_id': req.context['user_id']
        }, strict=False)
        command_name = type(command).__name__

        if not command.is_valid():
            raise falcon.HTTPError(
                status=falcon.HTTP_400,
                title='Invalid command',
                description="{} validation failed due to {}".format(command_name, command.validation_errors())
            )

        try:
            result = self._command_bus.execute(command)
            res.status = falcon.HTTP_200
            res.body = json_response(result)
        except Exception as e:
            raise falcon.HTTPError(
                status=falcon.HTTP_400,
                title='Failed to execute {}'.format(command_name),
                description=str(e)
            )

        #     # TODO: Handle app exception
        #     pass
