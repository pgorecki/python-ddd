from dataclasses import dataclass

from modules.catalog.application import catalog_module
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.events import ListingDraftCreatedEvent
from modules.catalog.domain.repositories import ListingRepository
from seedwork.application.command_handlers import CommandResult
from lato import Command, TransactionContext
from seedwork.domain.value_objects import GenericUUID, Money


class CreateListingDraftCommand(Command):
    """A command for creating new listing in draft state"""

    listing_id: GenericUUID
    title: str
    description: str
    ask_price: Money
    seller_id: GenericUUID


@catalog_module.handler(CreateListingDraftCommand)
def create_listing_draft(
    command: CreateListingDraftCommand, repository: ListingRepository, publish
):
    listing = Listing(
        id=command.listing_id,
        title=command.title,
        description=command.description,
        ask_price=command.ask_price,
        seller_id=command.seller_id,
    )
    repository.add(listing)
    publish(ListingDraftCreatedEvent(listing_id=listing.id))
