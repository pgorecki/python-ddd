from datetime import datetime, timedelta

from modules.bidding.domain.entities import Listing
from modules.bidding.domain.value_objects import Seller
from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.application.decorators import domain_event_handler


@domain_event_handler
def when_listing_is_published_start_auction(
    event: ListingPublishedEvent, listing_repository
):
    listing = Listing(
        id=event.listing_id,
        seller=Seller(id=event.seller_id),
        initial_price=event.ask_price,
        starts_at=datetime.now(),
        ends_at=datetime.now() + timedelta(days=7),
    )
    listing_repository.add(listing)
