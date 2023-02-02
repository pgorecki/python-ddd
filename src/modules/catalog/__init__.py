from modules.catalog.application.command import (
    CreateListingDraftCommand,
    DeleteListingDraftCommand,
    PublishListingCommand,
    UpdateListingDraftCommand,
)
from modules.catalog.application.query import (
    GetAllListings,
    GetListingDetails,
    GetListingsOfSeller,
)
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from seedwork.application.modules import BusinessModule


class CatalogModule(BusinessModule):
    supported_commands = (
        CreateListingDraftCommand,
        UpdateListingDraftCommand,
        DeleteListingDraftCommand,
        PublishListingCommand,
    )
    supported_queries = (GetAllListings, GetListingDetails, GetListingsOfSeller)

    def configure_unit_of_work(self, uow):
        """Here we have a chance to add extra UOW attributes to be injected into command/query handers"""
        uow.listing_repository = PostgresJsonListingRepository(
            db_session=uow.db_session
        )
