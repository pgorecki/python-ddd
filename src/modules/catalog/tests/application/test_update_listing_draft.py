import pytest

from modules.catalog.application.command.update_listing_draft import (
    UpdateListingDraftCommand,
    update_listing_draft,
)
from modules.catalog.domain.entities import Listing
from seedwork.domain.value_objects import UUID, Money
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
        seller_id=UUID.v4(),
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
    result = update_listing_draft(command, repository)

    # assert
    assert result.is_success()
