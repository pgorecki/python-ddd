from dataclasses import dataclass
from typing import List
from seedwork.domain.entities import AggregateRoot
from seedwork.domain.value_objects import Money, UUID
from modules.catalog.domain.events import ListingDraftUpdatedEvent, ListingPublishedEvent, DomainEvent
from modules.catalog.domain.rules import ListingPriceMustBeGreaterThanZero
from .value_objects import ListingStatus


@dataclass
class Listing(AggregateRoot):
    title: str
    description: str
    price: Money
    seller_id: UUID
    status = ListingStatus.DRAFT

    def change_main_attributes(self, title: str, description: str, price: Money) -> List[DomainEvent]:
        self.title = title
        self.description = description
        self.price = price

        return [ListingDraftUpdatedEvent(listing_id=self.id)]

    def publish(self) -> List[DomainEvent]:
        self.check_rule(ListingPriceMustBeGreaterThanZero(price=self.price))
        self.status = ListingStatus.PUBLISHED
        return [ListingPublishedEvent(listing_id=self.id)]

@dataclass
class Seller(AggregateRoot):
    id: UUID
    is_new: bool = True
    currently_published_listings_count: int = 0

    def publish_listing(self, listing) -> List[DomainEvent]:
        self.check_rule(ListingPriceMustBeGreaterThanZero(price=listing.price))
        # self.check_rule(ListingMustBeInDraftState(listing.status))
        # self.check_rule(SellerMustBeEligibleForAddingNextListing(self))
        return listing.publish()

