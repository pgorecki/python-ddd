import pytest

from modules.catalog.application.command.update_listing_draft import (
    UpdateListingDraftCommand,
    update_listing_draft,
)
from modules.catalog.domain.entities import Listing
from seedwork.domain.value_objects import GenericUUID, Money
from seedwork.infrastructure.repository import InMemoryRepository


@pytest.mark.unit
def test_update_listing_draft():
    # arrange
    repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=GenericUUID.next_id(),
    )
    repository.add(listing)

    command = UpdateListingDraftCommand(
        listing_id=listing.id,
        title="Tiny golden dragon",
        description=listing.description,
        ask_price=listing.ask_price,
        modify_user_id=listing.seller_id,
    )

    # act
    update_listing_draft(command, repository)

    # assert
    assert listing.title == "Tiny golden dragon"


@pytest.mark.skip(
    "UpdateListingDraftCommand with optional fields is not yet implemented"
)
@pytest.mark.unit
def test_partially_update_listing_draft():
    # arrange
    repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=GenericUUID.next_id(),
    )
    repository.add(listing)

    # act
    command = UpdateListingDraftCommand(
        # only 2 fields should be updated, but all are required in a command
        listing_id=listing.id,
        title="Tiny golden dragon",
    )
    update_listing_draft(command, repository)

    # assert
    assert repository.get_by_id(listing.id).title == "Tiny golden dragon"
