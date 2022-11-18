from modules.catalog.domain.repositories import ListingRepository
from seedwork.application.decorators import query_handler
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult


class GetAllListings(Query):
    ...


@query_handler
def get_all_listings(
    query: GetAllListings, listing_repository: ListingRepository
) -> QueryResult:
    queryset = listing_repository.session.query(listing_repository.model)
    result = [dict(id=row.id, **row.data) for row in queryset.all()]
    # TODO: add error handling
    return QueryResult.ok(result)
