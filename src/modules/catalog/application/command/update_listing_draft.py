from seedwork.application.commands import Command
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler
from seedwork.domain.value_objects import Money, UUID
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository


class UpdateListingDraftCommand(Command):
    """A command for updating a listing"""

    listing_id: UUID
    title: str
    description: str
    price: Money
    modify_user_id: UUID


@command_handler
def update_listing_draft(
    command: UpdateListingDraftCommand, repository: ListingRepository
) -> CommandResult:
    listing: Listing = repository.get_by_id(command.listing_id)
    events = listing.change_main_attributes(
        title=command.title, description=command.description, price=command.price
    )
    repository.update(listing)
    return CommandResult.ok(events=events)
