from seedwork.infrastructure.repository import InMemoryRepository
from modules.bidding.module import BiddingModule
from modules.bidding.application.query.get_pastdue_listings import (
    GetPastdueListingsQuery,
)


class DummyEventPublisher:
    ...


def test_module():
    module = BiddingModule(
        event_publisher=DummyEventPublisher(), listing_repository=InMemoryRepository()
    )

    query = GetPastdueListingsQuery()
    result = module.execute_query(query)

    assert result.is_ok()
    assert result.get_result() == []
