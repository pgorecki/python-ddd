from seedwork.domain.value_objects import UUID
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.application.decorators import query_handler
from modules.catalog.domain.repositories import ListingRepository


class GetListingsOfSeller(Query):
    seller_id: UUID


@query_handler
def get_listings_of_seller(
    query: GetListingsOfSeller, listing_repository: ListingRepository
) -> QueryResult:
    queryset = listing_repository.session.query(listing_repository.model)  # .filter(
    #     listing_repository.model.data['seller'].astext.cast(UUID) == query.seller_id
    # )
    result = [dict(id=row.id, **row.data) for row in queryset.all()]
    return QueryResult.ok(result)
