from datetime import datetime, timedelta

from modules.bidding.application import bidding_module
from modules.bidding.domain.entities import Listing
from modules.bidding.domain.events import BidWasPlaced
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Seller
from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.application.events import IntegrationEvent
from seedwork.domain.value_objects import GenericUUID


class SendEmailToSellerThatBidWasPlaced(IntegrationEvent):
    listing_id: GenericUUID
    bidder_id: GenericUUID


@bidding_module.domain_event_handler
def notify_outbid_winner(event: BidWasPlaced, logger):
    logger.info(f"Message from a handler: Listing {event.listing_id} was published")


@bidding_module.domain_event_handler
def notify_seller_of_new_bid(event: BidWasPlaced, logger):
    logger.info("New bid was placed")
    return SendEmailToSellerThatBidWasPlaced(
        listing_id=event.listing_id, bidder_id=event.bidder_id
    )


@bidding_module.domain_event_handler
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
