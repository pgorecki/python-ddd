from modules.bidding.application import bidding_module
from modules.bidding.domain.entities import Listing
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Bidder
from seedwork.application.commands import Command
from seedwork.domain.value_objects import GenericUUID


class RetractBidCommand(Command):
    listing_id: GenericUUID
    bidder_id: GenericUUID


@bidding_module.handler(RetractBidCommand)
def retract_bid(
    command: RetractBidCommand, listing_repository: ListingRepository
):
    bidder = Bidder(id=command.bidder_id)

    listing: Listing = listing_repository.get_by_id(id=command.listing_id)
    listing.retract_bid_of(bidder)
