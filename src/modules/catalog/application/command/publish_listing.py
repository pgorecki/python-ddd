from dataclasses import dataclass

from modules.catalog.domain.entities import Listing, Seller
from modules.catalog.domain.repositories import ListingRepository, SellerRepository
from modules.catalog.domain.value_objects import ListingId, SellerId
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.decorators import command_handler


@dataclass
class PublishListingCommand(Command):
    """A command for publishing a draft of a listing"""

    listing_id: ListingId
    seller_id: SellerId


@command_handler
def publish_listing(
    command: PublishListingCommand,
    listing_repository: ListingRepository,
    seller_repository: SellerRepository,
):
    seller: Seller = seller_repository.get_by_id(command.seller_id)
    listing: Listing = listing_repository.get_by_id(command.listing_id)

    events = seller.publish_listing(listing)

    return CommandResult.success(entity_id=listing.id, events=events)
