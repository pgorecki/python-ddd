from dataclasses import dataclass

from seedwork.domain.entities import AggregateRoot, Entity


@dataclass
class PersonEntity(Entity):
    name: str


@dataclass
class PersonAggregate(AggregateRoot):
    name: str


def test_entity():
    bob = PersonEntity(id=PersonEntity.next_id(), name="Bob")
    assert bob.id is not None


def test_aggregate():
    bob = PersonAggregate(id=PersonEntity.next_id(), name="Bob")
    assert bob.id is not None
