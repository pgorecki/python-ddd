import pytest

from modules.catalog.application.command.publish_listing import (
    PublishListingCommand,
    publish_listing,
)
from modules.catalog.domain.entities import Listing, Seller
from modules.catalog.domain.value_objects import ListingStatus
from seedwork.domain.value_objects import Money
from seedwork.infrastructure.repository import InMemoryRepository


@pytest.mark.unit
def test_publish_listing():
    # arrange
    seller_repository = InMemoryRepository()
    seller = Seller(id=Seller.next_id())
    seller_repository.add(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=seller.id,
    )
    listing_repository.add(listing)

    command = PublishListingCommand(
        listing_id=listing.id,
        seller_id=seller.id,
    )

    # act
    result = publish_listing(
        command,
        listing_repository=listing_repository,
        seller_repository=seller_repository,
    )

    # assert
    assert result.is_success()
    assert listing.status == ListingStatus.PUBLISHED


@pytest.mark.unit
def test_publish_listing_and_break_business_rule():
    # arrange
    seller_repository = InMemoryRepository()
    seller = Seller(id=Seller.next_id())
    seller_repository.add(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(0),  # this will break the rule
        seller_id=seller.id,
    )
    listing_repository.add(listing)

    command = PublishListingCommand(
        listing_id=listing.id,
        seller_id=seller.id,
    )

    # act
    result = publish_listing(
        command,
        listing_repository=listing_repository,
        seller_repository=seller_repository,
    )

    # assert
    assert result.has_errors()
