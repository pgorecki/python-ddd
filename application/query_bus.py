from application.queries import Query, QueryResult


class QueryBus(object):
    """
    Query bus is a central place for querying the data.
    It offers some benefits over direct querying the database and/or repositories:
    - in-memory bus can be replaced with persistent one, so multiple apps can share one bus
    - it can be used by multiple clients: web controller, console app, etc.
    - we can provide rate limiting and DoS protection
    - we can cache query results
    """

    def __init__(self, query_handler_factory):
        self._query_handler_factory = query_handler_factory

    def get_handler_for_query(self, query: Query):
        query_class_name = type(query).__name__
        return self._query_handler_factory(query_class_name)

    def execute(self, query: Query) -> QueryResult:
        handler = self.get_handler_for_query(query)
        return handler.handle(query)
