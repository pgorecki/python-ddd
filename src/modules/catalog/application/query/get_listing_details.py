from seedwork.domain.value_objects import UUID
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.application.decorators import query_handler

from modules.catalog.domain.repositories import ListingRepository


class GetListingDetails(Query):
    listing_id: UUID


@query_handler
def get_listing_details(
    query: GetListingDetails, listing_repository: ListingRepository
) -> QueryResult:
    queryset = listing_repository.session.query(listing_repository.model).filter_by(
        id=query.listing_id
    )
    result = [dict(id=row.id, **row.data) for row in queryset.all()][0]
    return QueryResult.ok(result)
