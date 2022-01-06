from datetime import datetime
from modules.bidding.domain.repositories import ListingRepository
from seedwork.application.queries import Query, Field
from seedwork.application.decorators import query_handler


class GetPastdueListingsQuery(Query):
    now: datetime = Field(default_factory=datetime.utcnow)


@query_handler
def get_past_due_listings(
    query: GetPastdueListingsQuery, listing_repository: ListingRepository
):
    # TODO: not yet implemented
    return []
