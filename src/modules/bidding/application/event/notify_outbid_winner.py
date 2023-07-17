from modules.bidding.application import bidding_module
from modules.bidding.domain.events import BidWasPlaced
from seedwork.infrastructure.logging import logger


@bidding_module.domain_event_handler
def notify_outbid_winner(event: BidWasPlaced):
    logger.info(f"Message from a handler: Listing {event.listing_id} was published")
