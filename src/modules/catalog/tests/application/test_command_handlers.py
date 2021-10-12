from modules.catalog.application.create_listing_draft.commands import (
    CreateListingDraftCommand,
    UpdateListingDraftCommand,
    PublishListingCommand,
)
from modules.catalog.application.command_handlers import (
    create_listing_draft,
    update_listing_draft,
    publish_listing,
)
from modules.catalog.domain.entities import Listing, Seller
from modules.catalog.domain.value_objects import ListingStatus
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

    # assert
    assert result.is_ok()


def test_publish_listing():
    # arrange
    seller_id = UUID.v4()
    seller_repository = InMemoryRepository()
    seller = Seller()
    seller_repository.insert(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=1,
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
    assert result.is_ok()
    assert listing.status == ListingStatus.PUBLISHED


def test_publish_listing_and_break_business_rule():
    # arrange
    seller_id = UUID.v4()
    seller_repository = InMemoryRepository()
    seller = Seller()
    seller_repository.insert(seller)

    listing_repository = InMemoryRepository()
    listing = Listing(
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=0,  # this will break the rule
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
