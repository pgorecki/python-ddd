from dataclasses import dataclass

from modules.bidding.application import bidding_module
from modules.bidding.domain.repositories import ListingRepository
from modules.bidding.domain.value_objects import Bid, Bidder, Money
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.domain.value_objects import GenericUUID


@dataclass
class PlaceBidCommand(Command):
    listing_id: GenericUUID
    bidder_id: GenericUUID
    amount: int  # todo: Decimal
    currency: str = "USD"


@bidding_module.command_handler
def place_bid(
    command: PlaceBidCommand, listing_repository: ListingRepository
) -> CommandResult:
    bidder = Bidder(id=command.bidder_id)
    bid = Bid(bidder=bidder, max_price=Money(amount=command.amount))

    listing = listing_repository.get_by_id(command.listing_id)
    listing.place_bid(bid)
