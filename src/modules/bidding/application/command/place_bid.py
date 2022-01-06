from decimal import Decimal
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler
from src.modules.bidding.domain.entities import Listing
from src.modules.bidding.domain.value_objects import Bid, Bidder, Money
from src.modules.bidding.domain.repositories import ListingRepository


class PlaceBidCommand:
    listing_id: str
    bidder_id: str
    amount: Decimal
    currency: str = "USD"


@command_handler
def place_bid(command: PlaceBidCommand, repository: ListingRepository) -> CommandResult:
    bidder = Bidder(id=command.bidder_id)
    bid = Bid(bidder=bidder, price=Money(command.amount))

    listing: Listing = repository.get_by_id(id=command.listing_id)
    events = listing.place_bid(bid)
    repository.update(listing)

    return CommandResult.ok(events=events)
