from dataclasses import dataclass

from modules.catalog.domain.events import (
    DomainEvent,
    ListingDraftUpdatedEvent,
    ListingPublishedEvent,
)
from modules.catalog.domain.rules import (
    ListingAskPriceMustBeGreaterThanZero,
    ListingMustBeDraft,
)
from seedwork.domain.entities import AggregateRoot
from seedwork.domain.value_objects import GenericUUID, Money

from .value_objects import ListingStatus


@dataclass(kw_only=True)
class Listing(AggregateRoot):
    title: str
    description: str
    ask_price: Money
    seller_id: GenericUUID
    status = ListingStatus.DRAFT

    def change_main_attributes(self, title: str, description: str, ask_price: Money):
        self.title = title
        self.description = description
        self.ask_price = ask_price
        self.register_event(ListingDraftUpdatedEvent(listing_id=self.id))

    def publish(self):
        """Instantly publish listing for sale"""
        self.check_rule(ListingMustBeDraft(status=self.status))
        self.check_rule(ListingAskPriceMustBeGreaterThanZero(ask_price=self.ask_price))
        self.status = ListingStatus.PUBLISHED
        self.register_event(
            ListingPublishedEvent(
                listing_id=self.id, ask_price=self.ask_price, seller_id=self.seller_id
            )
        )


@dataclass
class Seller(AggregateRoot):
    id: GenericUUID
    is_new: bool = True
    currently_published_listings_count: int = 0

    def publish_listing(self, listing) -> list[DomainEvent]:
        self.check_rule(
            ListingAskPriceMustBeGreaterThanZero(ask_price=listing.ask_price)
        )
        # self.check_rule(ListingMustBeInDraftState(listing.status))
        # self.check_rule(SellerMustBeEligibleForAddingNextListing(self))
        return listing.publish()
