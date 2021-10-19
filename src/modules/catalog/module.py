from seedwork.application.modules import BusinessModule

from .domain.repositories import ListingRepository

from modules.catalog.application.query.get_all_listings import (
    GetAllListings,
    get_all_listings,
)

from modules.catalog.application.query.get_listings_of_seller import (
    GetListingsOfSeller,
    get_listings_of_seller,
)

from modules.catalog.application.query.get_listing_details import (
    GetListingDetails,
    get_listing_details,
)

from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
    create_listing_draft,
)


class CatalogModule(BusinessModule):
    query_handlers = {
        GetAllListings: lambda self, q: get_all_listings(q, self.listing_repository),
        GetAllListings: lambda self, q: get_all_listings(q, self.listing_repository),
        GetListingDetails: lambda self, q: get_listing_details(
            q, self.listing_repository
        ),
        GetListingsOfSeller: lambda self, q: get_listings_of_seller(
            q, self.listing_repository
        ),
    }
    command_handlers = {
        CreateListingDraftCommand: lambda self, c: create_listing_draft(
            c, self.listing_repository
        ),
    }

    def __init__(
        self,
        listing_repository: ListingRepository,
    ) -> None:
        self.listing_repository = listing_repository

    @staticmethod
    def create(container):
        """Factory method for creating a module by using dependencies from a DI container"""
        return CatalogModule(
            logger=container.logger(),
            listing_repository=container.listing_repository(),
        )
