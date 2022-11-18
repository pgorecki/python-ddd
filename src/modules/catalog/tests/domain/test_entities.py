import pytest

from modules.catalog.domain.entities import Listing, Seller
from modules.catalog.domain.value_objects import ListingStatus
from seedwork.domain.exceptions import BusinessRuleValidationException
from seedwork.domain.value_objects import Money


def test_seller_publishes_listing_happy_path():
    seller = Seller(id=Seller.next_id())
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(1),
        seller_id=seller.id,
    )

    seller.publish_listing(listing)

    assert listing.status == ListingStatus.PUBLISHED


def test_seller_fails_to_publish_listing_with_zero_price():
    seller = Seller(id=Seller.next_id())
    listing = Listing(
        id=Listing.next_id(),
        title="Tiny dragon",
        description="Tiny dragon for sale",
        ask_price=Money(0),
        seller_id=seller.id,
    )

    with pytest.raises(BusinessRuleValidationException):
        seller.publish_listing(listing)
