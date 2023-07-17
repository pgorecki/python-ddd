import pytest

from modules.catalog.application.command.delete_listing_draft import (
    DeleteListingDraftCommand,
    delete_listing_draft,
)
from modules.catalog.domain.entities import Listing
from modules.catalog.domain.events import ListingDraftDeletedEvent
from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from seedwork.domain.value_objects import GenericUUID, Money
from seedwork.infrastructure.repository import InMemoryRepository


@pytest.mark.unit
def test_delete_listing_draft():
    # arrange
    seller_id = GenericUUID.next_id()
    repository = InMemoryRepository()
    listing_id = Listing.next_id()
    listing = Listing(
        id=listing_id,
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=seller_id,
    )
    repository.add(listing)

    command = DeleteListingDraftCommand(
        listing_id=listing.id,
        seller_id=seller_id,
    )

    # act
    result = delete_listing_draft(command, repository)

    # assert
    assert result.is_success()
    assert result.events == [ListingDraftDeletedEvent(listing_id=listing.id)]


@pytest.mark.integration
def test_delete_listing_draft_removes_from_database(db_session):
    seller_id = GenericUUID.next_id()
    repository = PostgresJsonListingRepository(db_session=db_session)
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=seller_id,
    )
    repository.add(listing)

    command = DeleteListingDraftCommand(
        listing_id=listing.id,
        seller_id=seller_id,
    )

    # act
    delete_listing_draft(command, repository)

    # assert
    assert repository.count() == 0
