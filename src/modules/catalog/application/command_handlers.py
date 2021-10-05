from modules.catalog.application.commands import (
    CreateListingDraftCommand,
    UpdateListingDraftCommand,
    PublishListingCommand,
)
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository, SellerRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


@command_handler
def create_listing_draft(
    command: CreateListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing = Listing(**command.dict())
    try:
        repository.insert(listing)
    except Exception as e:
        return CommandResult.error(message="Failed to create listing", exception=e)

    return CommandResult.ok(id=listing.id)


@command_handler
def update_listing_draft(
    command: UpdateListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing = repository.get_by_id(command.listing_id)
    listing.change_main_attributes(
        title=command.title, description=command.description, price=command.price
    )
    try:
        repository.update(listing)
    except:
        return CommandResult.error("Failed to update listing")

    return CommandResult.ok()


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
