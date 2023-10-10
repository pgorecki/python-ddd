import pytest

from modules.bidding.application.event import BidWasPlacedNotification
from modules.bidding.domain.events import BidWasPlaced
from seedwork.domain.value_objects import GenericUUID, Money


@pytest.mark.integration
def test_seller_is_notified_of_new_bid(app):
    with app.transaction_context() as ctx:
        chain = ctx.handle_domain_event(
            BidWasPlaced(
                listing_id=GenericUUID(int=1),
                bidder_id=GenericUUID(int=2),
                amount=Money(10),
            )
        )
        events = chain.triggered_events(BidWasPlacedNotification)

    assert len(events) == 1
