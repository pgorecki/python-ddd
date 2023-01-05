from dataclasses import dataclass

import pytest

from seedwork.domain.entities import AggregateRoot, Entity


@dataclass
class PersonEntity(Entity):
    name: str


@dataclass
class PersonAggregate(AggregateRoot):
    name: str


@pytest.mark.unit
def test_entity():
    bob = PersonEntity(id=PersonEntity.next_id(), name="Bob")
    assert bob.id is not None


@pytest.mark.unit
def test_aggregate():
    bob = PersonAggregate(id=PersonEntity.next_id(), name="Bob")
    assert bob.id is not None
