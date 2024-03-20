from modules.catalog.application import catalog_module
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository
from lato import Command
from seedwork.domain.value_objects import GenericUUID, Money


class UpdateListingDraftCommand(Command):
    """A command for updating a listing"""

    listing_id: GenericUUID
    title: str
    description: str
    ask_price: Money
    modify_user_id: GenericUUID


@catalog_module.handler(UpdateListingDraftCommand)
def update_listing_draft(
    command: UpdateListingDraftCommand, repository: ListingRepository
):
    listing: Listing = repository.get_by_id(command.listing_id)
    listing.change_main_attributes(
        title=command.title,
        description=command.description,
        ask_price=command.ask_price,
    )
