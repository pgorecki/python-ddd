import pytest
from modules.catalog.application.commands import (
    CreateListingDraftCommand,
    UpdateListingDraftCommand,
)
from modules.catalog.application.command_handlers import (
    create_listing_draft,
    update_listing_draft,
)
from modules.catalog.domain.entities import Listing
from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.domain.value_objects import UUID


def test_create_listing_draft():
    # arrange
    command = CreateListingDraftCommand(
        title="foo", description="bar", price=1, seller_id=UUID.v4()
    )
    repository = InMemoryRepository()

    # act
    result = create_listing_draft(command, repository)

    # assert
    assert repository.get_by_id(result.id).title == "foo"
    assert result.has_errors() is False


def test_update_listing_draft():
    # arrange
    repository = InMemoryRepository()
    listing = Listing(
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=1,
        seller_id=UUID.v4(),
    )
    repository.insert(listing)

    command = UpdateListingDraftCommand(
        listing_id=listing.id,
        title="Tiny golden dragon",
        description=listing.description,
        price=listing.price,
        modify_user_id=listing.seller_id,
    )

    # act
    result = update_listing_draft(command, repository)
    assert result.is_ok()
