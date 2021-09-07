from datetime import date
from typing import Any
from seedwork.domain.entities import Entity
from seedwork.domain.value_objects import Currency, UUID
from modules.catalog.domain.rules import ListingPriceMustBeGreaterThanZero
from .value_objects import ListingStatus


class Listing(Entity):
    title: str
    description: str
    price: Currency
    seller_id: UUID
    status = ListingStatus.DRAFT

    def change_main_attributes(self, title: str, description: str, price: Currency):
        self.title = title
        self.description = description
        self.price = price

    def publish(self):
        self.status = ListingStatus.PUBLISHED


class Seller(Entity):
    id: UUID
    is_new: bool = True
    currently_published_listings_count: int = 0

    def publish_listing(self, listing):
        self.check_rule(ListingPriceMustBeGreaterThanZero(price=listing.price))
        # self.check_rule(ListingMustBeInDraftState(listing.status))
        # self.check_rule(SellerMustBeEligibleForAddingNextListing(self))
        listing.publish()
