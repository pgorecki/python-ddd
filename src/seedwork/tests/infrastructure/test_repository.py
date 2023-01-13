from dataclasses import dataclass

import pytest

from seedwork.domain.entities import Entity
from seedwork.domain.exceptions import EntityNotFoundException
from seedwork.infrastructure.repository import InMemoryRepository


@dataclass
class Person(Entity):
    first_name: str
    last_name: str


@pytest.mark.unit
def test_InMemoryRepository_persist_one():
    # arrange
    person = Person(id=Person.next_id(), first_name="John", last_name="Doe")
    repository = InMemoryRepository()

    # act
    repository.add(person)

    # assert
    assert repository.get_by_id(person.id) == person


@pytest.mark.unit
def test_InMemoryRepository_persist_two():
    # arrange
    person1 = Person(id=Person.next_id(), first_name="John", last_name="Doe")
    person2 = Person(id=Person.next_id(), first_name="Mary", last_name="Doe")
    repository = InMemoryRepository()

    # act
    repository.add(person1)
    repository.add(person2)

    # assert
    assert repository.get_by_id(person1.id) == person1
    assert repository.get_by_id(person2.id) == person2


@pytest.mark.unit
def test_InMemoryRepository_get_by_id_raises_exception():
    repository = InMemoryRepository()
    with pytest.raises(EntityNotFoundException):
        repository.get_by_id(Person.next_id())


@pytest.mark.unit
def test_InMemoryRepository_remove_by_id_raises_exception():
    repository = InMemoryRepository()
    with pytest.raises(EntityNotFoundException):
        repository.remove_by_id(Person.next_id())
