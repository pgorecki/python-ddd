from seedwork.application.modules import BusinessModule
from seedwork.domain.events import EventPublisher
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.application.query.get_pastdue_listings import (
    GetPastdueListingsQuery,
    get_past_due_listings,
)


class BiddingModule(BusinessModule):
    query_handlers = {
        GetPastdueListingsQuery: lambda self, q: get_past_due_listings(
            q, listing_repository=self.listing_repository
        )
        # GetAllListings: lambda self, q: get_all_listings(q, self.listing_repository),
        # GetListingDetails: lambda self, q: get_listing_details(
        #     q, self.listing_repository
        # ),
        # GetListingsOfSeller: lambda self, q: get_listings_of_seller(
        #     q, self.listing_repository
        # ),
    }
    command_handlers = {
        # CreateListingDraftCommand: lambda self, c: create_listing_draft(
        #     c,
        #     self.event_publisher,
        #     self.listing_repository,
        # ),
    }

    def __init__(
        self,
        event_publisher: EventPublisher,
        listing_repository: ListingRepository,
    ) -> None:
        self.event_publisher = event_publisher
        self.listing_repository = listing_repository

    @staticmethod
    def create(container):
        """Factory method for creating a module by using dependencies from a DI container"""
        return BiddingModule(
            logger=container.logger(),
            event_publisher=container.event_publisher(),
            listing_repository=container.listing_repository(),
        )
