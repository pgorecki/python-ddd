from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.infrastructure.logging import logger


def do_nothing_when_listing_published(event: ListingPublishedEvent):
    logger.info(f"Message from a handler: Listing {event.listing_id} was published")
