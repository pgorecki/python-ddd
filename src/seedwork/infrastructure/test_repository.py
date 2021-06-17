from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.domain.entities import Entity


class Person(Entity):
    first_name: str
    last_name: str


def test_InMemoryRepository_persist_one():
    # arrange
    person = Person(first_name="John", last_name="Doe")
    repository = InMemoryRepository()

    # act
    repository.insert(person)

    # assert
    assert repository.get_by_id(person.id) == person


def test_InMemoryRepository_persist_two():
    # arrange
    person1 = Person(first_name="John", last_name="Doe")
    person2 = Person(first_name="Mary", last_name="Doe")
    repository = InMemoryRepository()

    # act
    repository.insert(person1)
    repository.insert(person2)

    # assert
    assert repository.get_by_id(person1.id) == person1
    assert repository.get_by_id(person2.id) == person2
