from modules.catalog.application.commands import (
    CreateListingDraftCommand,
    UpdateListingDraftCommand,
)
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


@command_handler
def create_listing_draft(
    command: CreateListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing = Listing(**command.dict())
    try:
        repository.insert(listing)
    except:
        return CommandResult.error("Failed to create listing")

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
