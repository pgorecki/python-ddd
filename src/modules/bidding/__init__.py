from modules.bidding.application.command import PlaceBidCommand, RetractBidCommand
from modules.bidding.application.query import GetPastdueListingsQuery
from modules.bidding.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from seedwork.application.modules import BusinessModule


class BiddingModule(BusinessModule):
    supported_commands = (PlaceBidCommand, RetractBidCommand)
    supported_queries = (GetPastdueListingsQuery,)
    supported_events = ()

    def configure_unit_of_work(self, uow):
        """Here we have a chance to add extra UOW attributes to be injected into command/query handers"""
        uow.listing_repository = PostgresJsonListingRepository(
            db_session=uow.db_session
        )
