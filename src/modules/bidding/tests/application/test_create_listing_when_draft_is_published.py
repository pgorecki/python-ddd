import pytest

from modules.bidding.domain.repositories import (
    ListingRepository as BiddingListingRepository,
)
from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.domain.value_objects import GenericUUID, Money


@pytest.mark.integration
def test_create_listing_on_draft_published_event(app, engine):
    listing_id = GenericUUID(int=1)
    app.publish(
            ListingPublishedEvent(
                listing_id=listing_id,
                seller_id=GenericUUID.next_id(),
                ask_price=Money(10),
            )
        )

    with app.transaction_context() as ctx:
        listing_repository = ctx[BiddingListingRepository]
        assert listing_repository.count() == 1
