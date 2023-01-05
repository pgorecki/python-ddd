from decimal import Decimal

from modules.bidding.domain.entities import Listing
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Bid, Bidder, Money
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.decorators import command_handler


class PlaceBidCommand(Command):
    listing_id: str
    bidder_id: str
    amount: Decimal
    currency: str = "USD"


@command_handler
def place_bid(
    command: PlaceBidCommand, listing_repository: ListingRepository
) -> CommandResult:
    bidder = Bidder(id=command.bidder_id)
    bid = Bid(bidder=bidder, price=Money(command.amount))

    listing: Listing = listing_repository.get_by_id(id=command.listing_id)
    listing.place_bid(bid)

    return CommandResult.ok()
