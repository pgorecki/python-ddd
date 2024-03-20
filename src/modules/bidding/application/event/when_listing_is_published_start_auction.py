from datetime import datetime, timedelta

from modules.bidding.application import bidding_module
from modules.bidding.domain.entities import Listing
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Seller
from modules.catalog.domain.events import ListingPublishedEvent


@bidding_module.handler(ListingPublishedEvent)
def when_listing_is_published_start_auction(
    event: ListingPublishedEvent, listing_repository: ListingRepository
):
    listing = Listing(
        id=event.listing_id,
        seller=Seller(id=event.seller_id),
        ask_price=event.ask_price,
        starts_at=datetime.now(),
        ends_at=datetime.now() + timedelta(days=7),
    )
    listing_repository.add(listing)
