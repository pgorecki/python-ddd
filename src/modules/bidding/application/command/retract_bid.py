from decimal import Decimal
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler
from src.modules.bidding.domain.entities import Listing
from src.modules.bidding.domain.value_objects import Bidder
from src.modules.bidding.domain.repositories import ListingRepository


class RetractBidCommand:
    listing_id: str
    bidder_id: str
    amount: Decimal
    currency: str = "USD"


@command_handler
def retract_bid(
    command: RetractBidCommand, repository: ListingRepository
) -> CommandResult:
    bidder = Bidder(id=command.bidder_id)

    listing: Listing = repository.get_by_id(id=command.listing_id)
    events = listing.retract_bid_of(bidder)
    repository.update(listing)

    return CommandResult.ok(events=events)
