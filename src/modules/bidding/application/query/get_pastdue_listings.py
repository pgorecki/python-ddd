from dataclasses import dataclass, field
from datetime import datetime

from modules.bidding.application import bidding_module
from modules.bidding.domain.repositories import ListingRepository
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult


@dataclass
class GetPastdueListings(Query):
    now: datetime = field(default_factory=datetime.utcnow)


@bidding_module.query_handler
def get_past_due_listings(
    query: GetPastdueListings, listing_repository: ListingRepository
) -> QueryResult:
    # TODO: not yet implemented
    return QueryResult([])
