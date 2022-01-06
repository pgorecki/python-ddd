from dataclasses import dataclass
from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import UUID


@dataclass
class ListingDraftCreatedEvent(DomainEvent):
    listing_id: UUID
