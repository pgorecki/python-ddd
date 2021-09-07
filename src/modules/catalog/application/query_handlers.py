from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryHandler, QueryResult
from seedwork.application.decorators import query_handler

from ..application.queries import GetAllListingsQuery, GetListingsOfSellerQuery
from ..domain.repositories import ListingRepository


@query_handler
def get_all_listings(query: GetAllListingsQuery) -> QueryResult:
    sql = "SELECT * FROM listings"
    data = ["foo", "bar"]
    return QueryResult.ok(data)


@query_handler
def get_listings_of_seller(query: GetListingsOfSellerQuery) -> QueryHandler:
    data = ["foo"]
    return QueryResult.ok(data)
