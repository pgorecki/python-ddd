from dataclasses import dataclass

from modules.catalog.application import catalog_module
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.value_objects import ListingId
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command


@dataclass
class PublishListingDraftCommand(Command):
    """A command for publishing a draft of a listing"""

    listing_id: ListingId
    # seller_id: SellerId


@catalog_module.command_handler
def publish_listing_draft(
    command: PublishListingDraftCommand,
    listing_repository: ListingRepository,
):
    listing: Listing = listing_repository.get_by_id(command.listing_id)

    events = listing.publish()

    listing_repository.persist_all()

    return CommandResult.success(entity_id=listing.id, events=events)
