from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import GenericUUID, Money


class ListingDraftCreatedEvent(DomainEvent):
    listing_id: GenericUUID


class ListingDraftUpdatedEvent(DomainEvent):
    listing_id: GenericUUID


class ListingDraftDeletedEvent(DomainEvent):
    listing_id: GenericUUID


class ListingPublishedEvent(DomainEvent):
    listing_id: GenericUUID
    seller_id: GenericUUID
    ask_price: Money
