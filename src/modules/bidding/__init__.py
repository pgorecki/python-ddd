from modules.bidding.application.command import PlaceBidCommand, RetractBidCommand
from modules.bidding.application.event import when_listing_is_published_start_auction
from modules.bidding.application.query import GetBiddingDetails, GetPastdueListings
from modules.bidding.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from seedwork.application.modules import BusinessModule


class BiddingModule(BusinessModule):
    supported_commands = (PlaceBidCommand, RetractBidCommand)
    supported_queries = (GetPastdueListings, GetBiddingDetails)
    event_handlers = (when_listing_is_published_start_auction,)

    def configure_unit_of_work(self, uow):
        """Here we have a chance to add extra UOW attributes to be injected into command/query handlers"""
        uow.listing_repository = PostgresJsonListingRepository(
            db_session=uow.db_session
        )
