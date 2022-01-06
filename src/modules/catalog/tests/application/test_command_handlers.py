from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
    create_listing_draft,
)
from modules.catalog.application.command.update_listing_draft import (
    UpdateListingDraftCommand,
    update_listing_draft,
)
from modules.catalog.application.command.publish_listing import (
    PublishListingCommand,
    publish_listing,
)

from modules.catalog.domain.entities import Listing, Seller
from modules.catalog.domain.value_objects import ListingStatus
from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.domain.value_objects import UUID, Money


def test_create_listing_draft():
    # arrange
    command = CreateListingDraftCommand(
        title="foo", description="bar", price=Money(1), seller_id=Seller.next_id()
    )
    repository = InMemoryRepository()

    # act
    result = create_listing_draft(command, repository)
    
    # assert
    assert repository.get_by_id(result.result).title == "foo"
    assert result.has_errors() is False


def test_update_listing_draft():
    # arrange
    repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=Money(1),
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

    # assert
    assert result.is_ok()


def test_publish_listing():
    # arrange
    seller_repository = InMemoryRepository()
    seller = Seller(id=Seller.next_id())
    seller_repository.insert(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=Money(1),
        seller_id=seller.id,
    )
    listing_repository.insert(listing)

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
    
    print(result)

    # assert
    assert result.is_ok()
    assert listing.status == ListingStatus.PUBLISHED


def test_publish_listing_and_break_business_rule():
    # arrange
    seller_repository = InMemoryRepository()
    seller = Seller(id=Seller.next_id())
    seller_repository.insert(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=Money(0),  # this will break the rule
        seller_id=seller.id,
    )
    listing_repository.insert(listing)

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
