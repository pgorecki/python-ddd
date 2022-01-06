from dataclasses import dataclass, field
from .value_objects import UUID
from .mixins import BusinessRuleValidationMixin


@dataclass
class Entity:
    id: UUID = field(hash=True)

    @classmethod
    def next_id(cls) -> UUID:
        return UUID.v4()


@dataclass
class AggregateRoot(BusinessRuleValidationMixin, Entity):
    """Consits of 1+ entities. Spans transaction boundaries."""
