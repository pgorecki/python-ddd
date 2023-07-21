from modules.catalog.application import catalog_module
from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.infrastructure.logging import logger


@catalog_module.domain_event_handler
def do_nothing_when_listing_published(event: ListingPublishedEvent):
    logger.info(f"Message from a handler: Listing {event.listing_id} was published")
