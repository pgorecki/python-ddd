from seedwork.application.commands import Command
from seedwork.domain.value_objects import UUID, Money
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository


class CreateListingDraftCommand(Command):
    """A command for creating new listing in draft state"""

    title: str
    description: str
    price: Money
    seller_id: UUID


@command_handler
def create_listing_draft(
    command: CreateListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing = Listing(id=repository.next_id(), **command.dict())
    try:
        repository.insert(listing)
    except Exception as e:
        return CommandResult.failed(message="Failed to create listing", exception=e)

    return CommandResult.ok(result=listing.id)
