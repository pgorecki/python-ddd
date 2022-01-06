from datetime import datetime
from seedwork.application.queries import Query, Field
from seedwork.application.query_handlers import QueryResult
from seedwork.application.decorators import query_handler
from modules.bidding.domain.repositories import ListingRepository


class GetPastdueListingsQuery(Query):
    now: datetime = Field(default_factory=datetime.utcnow)


@query_handler
def get_past_due_listings(
    query: GetPastdueListingsQuery, listing_repository: ListingRepository
) -> QueryResult:
    # TODO: not yet implemented
    return QueryResult([])
