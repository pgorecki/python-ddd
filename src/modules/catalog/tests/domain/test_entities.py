import pytest
from modules.catalog.domain.entities import Seller, Listing
from modules.catalog.domain.value_objects import ListingStatus
from seedwork.domain.exceptions import BusinessRuleValidationException


def test_seller_publishes_listing_happy_path():
    seller = Seller()
    listing = Listing(
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=1,
        seller_id=seller.id,
    )

    seller.publish_listing(listing)

    assert listing.status == ListingStatus.PUBLISHED


def test_seller_fails_to_publish_listing_with_zero_price():
    seller = Seller()
    listing = Listing(
        title="Tiny dragon",
        description="Tiny dragon for sale",
        price=0,
        seller_id=seller.id,
    )

    with pytest.raises(BusinessRuleValidationException):
        seller.publish_listing(listing)
