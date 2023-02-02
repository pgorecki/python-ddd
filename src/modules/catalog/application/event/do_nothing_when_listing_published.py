from modules.catalog import CatalogModule
from modules.catalog.domain.events import ListingPublishedEvent


def do_nothing_when_listing_published(
    event: ListingPublishedEvent, module: CatalogModule
):
    print("Listing has been published")
