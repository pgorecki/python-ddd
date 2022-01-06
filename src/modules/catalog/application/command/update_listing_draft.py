from seedwork.application.commands import Command
from seedwork.domain.value_objects import Money, UUID
from modules.catalog.domain.repositories import ListingRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


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
    listing = repository.get_by_id(command.listing_id)
    listing.change_main_attributes(
        title=command.title, description=command.description, price=command.price
    )
    try:
        repository.update(listing)
    except:
        return CommandResult.error("Failed to update listing")

    return CommandResult.ok()
