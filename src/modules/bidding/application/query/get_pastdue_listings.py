from datetime import datetime

from modules.bidding.domain.repositories import ListingRepository
from seedwork.application.decorators import query_handler
from seedwork.application.queries import Field, Query
from seedwork.application.query_handlers import QueryResult


class GetPastdueListingsQuery(Query):
    now: datetime = Field(default_factory=datetime.utcnow)


@query_handler
def get_past_due_listings(
    query: GetPastdueListingsQuery, listing_repository: ListingRepository
) -> QueryResult:
    # TODO: not yet implemented
    return QueryResult([])
