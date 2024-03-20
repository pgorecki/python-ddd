from dataclasses import dataclass

from modules.catalog.application import catalog_module
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.events import ListingDraftDeletedEvent
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.rules import (
    OnlyListingOwnerCanDeleteListing,
    PublishedListingMustNotBeDeleted,
)
from seedwork.application.command_handlers import CommandResult
from lato import Command, TransactionContext
from seedwork.domain.mixins import check_rule
from seedwork.domain.value_objects import GenericUUID


class DeleteListingDraftCommand(Command):
    """A command for deleting a listing"""

    listing_id: GenericUUID
    seller_id: GenericUUID


@catalog_module.handler(DeleteListingDraftCommand)
def delete_listing_draft(
    command: DeleteListingDraftCommand, repository: ListingRepository, publish
):
    listing: Listing = repository.get_by_id(command.listing_id)
    check_rule(
        OnlyListingOwnerCanDeleteListing(
            listing_seller_id=listing.seller_id, current_seller_id=command.seller_id
        )
    )
    check_rule(PublishedListingMustNotBeDeleted(status=listing.status))
    repository.remove(listing)
    publish(ListingDraftDeletedEvent(listing_id=listing.id))
