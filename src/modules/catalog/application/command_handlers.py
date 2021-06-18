from modules.catalog.application.commands import (
    CreateListingDraftCommand,
)
from modules.catalog.domain.entities import Listing
from seedwork.application.commands import Command
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


@command_handler
def create_listing_draft(
    command: CreateListingDraftCommand, repository
) -> CommandResult:
    listing = Listing(**command.dict())
    try:
        repository.insert(listing)
    except:
        return CommandResult.error("Failed to add item")

    return CommandResult.ok(id=listing.id)
