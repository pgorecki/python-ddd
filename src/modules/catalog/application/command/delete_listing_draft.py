from dataclasses import dataclass

from modules.catalog.domain.entities import Listing
from modules.catalog.domain.events import ListingDraftDeletedEvent
from modules.catalog.domain.repositories import ListingRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.decorators import command_handler
from seedwork.domain.value_objects import UUID


@dataclass
class DeleteListingDraftCommand(Command):
    """A command for updating a listing"""

    listing_id: UUID


@command_handler
def delete_listing_draft(
    command: DeleteListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing: Listing = repository.get_by_id(command.listing_id)
    repository.remove(listing)
    return CommandResult.success(
        entity_id=listing.id, events=[ListingDraftDeletedEvent(listing_id=listing.id)]
    )
