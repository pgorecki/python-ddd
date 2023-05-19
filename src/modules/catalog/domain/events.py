from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import UUID, Money


class ListingDraftCreatedEvent(DomainEvent):
    listing_id: UUID


class ListingDraftUpdatedEvent(DomainEvent):
    listing_id: UUID


class ListingDraftDeletedEvent(DomainEvent):
    listing_id: UUID


class ListingPublishedEvent(DomainEvent):
    listing_id: UUID
    seller_id: UUID
    ask_price: Money
