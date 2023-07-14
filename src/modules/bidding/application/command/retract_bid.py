from modules.bidding.application import bidding_module
from modules.bidding.domain.entities import Listing
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Bidder
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.domain.value_objects import GenericUUID


class RetractBidCommand(Command):
    listing_id: GenericUUID
    bidder_id: GenericUUID


@bidding_module.command_handler
def retract_bid(
    command: RetractBidCommand, listing_repository: ListingRepository
) -> CommandResult:
    bidder = Bidder(id=command.bidder_id)

    listing: Listing = listing_repository.get_by_id(id=command.listing_id)
    event = listing.retract_bid_of(bidder)

    return CommandResult.success(event=event)
