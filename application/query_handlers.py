from application.queries import GetItemsQuery, QueryResult, QueryResultStatus

class GetItemsQueryHandler(object):
    def __init__(self, items_repository):
        self._items_repository = items_repository

    def handle(self, query: GetItemsQuery):
        data = self._items_repository.get_all()
        return QueryResult(status=QueryResultStatus.OK, data=data)