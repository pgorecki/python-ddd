from seedwork.application.commands import Command
from seedwork.domain.value_objects import UUID
from modules.catalog.domain.repositories import ListingRepository, SellerRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


class PublishListingCommand(Command):
    """A command for publishing a listing in draft state"""

    listing_id: UUID
    seller_id: UUID


@command_handler
def publish_listing(
    command: PublishListingCommand,
    listing_repository: ListingRepository,
    seller_repository: SellerRepository,
):
    listing = listing_repository.get_by_id(command.listing_id)
    seller = seller_repository.get_by_id(command.seller_id)

    seller.publish_listing(listing)

    # TODO: for now we need to manually persist the changes, but it should be handled automatically using "Unit of Work"
    listing_repository.update(listing)

    return CommandResult.ok()
