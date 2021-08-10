from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.application.decorators import query_handler

from ..application.queries import GetAllListingsQuery
from ..domain.repositories import ListingRepository


@query_handler
def get_all_listings(query: GetAllListingsQuery, sql_connection) -> QueryResult:
    sql = "SELECT * FROM listings"
    data = sql_connection.execute(sql)
    return QueryResult.ok(data)
