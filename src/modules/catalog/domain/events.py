from dataclasses import dataclass
from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import UUID


class ListingDraftCreatedEvent(DomainEvent):
    listing_id: UUID


class ListingDraftUpdatedEvent(DomainEvent):
    listing_id: UUID


class ListingPublishedEvent(DomainEvent):
    listing_id: UUID
