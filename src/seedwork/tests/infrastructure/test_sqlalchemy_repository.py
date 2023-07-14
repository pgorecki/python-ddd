import uuid
from dataclasses import dataclass

import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from sqlalchemy_utils import UUIDType

from seedwork.domain.entities import Entity
from seedwork.domain.exceptions import EntityNotFoundException
from seedwork.infrastructure.data_mapper import DataMapper
from seedwork.infrastructure.database import Base
from seedwork.infrastructure.repository import SqlAlchemyGenericRepository


@dataclass
class Person(Entity):
    """Domain object"""

    first_name: str
    last_name: str


class PersonModel(Base):
    """Data model for a domain object"""

    __tablename__ = "person"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)


class PersonDataMapper(DataMapper):
    def model_to_entity(self, instance: PersonModel) -> Person:
        return Person(
            id=instance.id,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )

    def entity_to_model(self, entity: Person) -> PersonModel:
        return PersonModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
        )


class PersonSqlAlchemyRepository(SqlAlchemyGenericRepository):
    mapper_class = PersonDataMapper
    model_class = PersonModel


@pytest.mark.integration
def test_sqlalchemy_repository_persist(db_session):
    # arrange
    person = Person(id=Person.next_id(), first_name="John", last_name="Doe")
    repository = PersonSqlAlchemyRepository(db_session=db_session)

    # act
    repository.add(person)

    # assert
    assert repository.count() == 1


@pytest.mark.integration
def test_sqlalchemy_repository_get_by_id(engine):
    # arrange
    person_id = Person.next_id()

    with Session(engine) as db_session:
        person1 = Person(id=person_id, first_name="John", last_name="Doe")
        repository1 = PersonSqlAlchemyRepository(db_session=db_session)
        repository1.add(person1)
        db_session.commit()

    # act - in separate session
    with Session(engine) as db_session:
        repository2 = PersonSqlAlchemyRepository(db_session=db_session)
        person2 = repository2.get_by_id(person_id)

    # assert
    assert person1 == person2


@pytest.mark.integration
def test_sqlalchemy_repository_update(engine):
    # arrange
    person_id = Person.next_id()

    with Session(engine) as db_session:
        person = Person(id=person_id, first_name="John", last_name="Doe")
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        repository.add(person)
        db_session.commit()

    # act
    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        person = repository.get_by_id(person_id)
        person.first_name = "Johnny"
        repository.persist_all()
        db_session.commit()

    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        person = repository.get_by_id(person_id)
        assert person.first_name == "Johnny"


@pytest.mark.integration
def test_sqlalchemy_repository_remove_by_id(engine):
    # arrange
    person_id = Person.next_id()

    with Session(engine) as db_session:
        person = Person(id=person_id, first_name="John", last_name="Doe")
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        repository.add(person)
        db_session.commit()

    # act
    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        repository.remove_by_id(person_id)
        db_session.commit()

    # assert
    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        assert repository.count() == 0


@pytest.mark.integration
def test_sqlalchemy_repository_remove(engine):
    # arrange
    person_id = Person.next_id()

    with Session(engine) as db_session:
        person = Person(id=person_id, first_name="John", last_name="Doe")
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        repository.add(person)
        db_session.commit()

    # act
    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        person = repository.get_by_id(person_id)
        repository.remove(person)
        db_session.commit()

    # assert
    with Session(engine) as db_session:
        repository = PersonSqlAlchemyRepository(db_session=db_session)
        assert repository.count() == 0


@pytest.mark.integration
def test_sqlalchemy_repository_get_by_id_raises_exception(db_session):
    repository = PersonSqlAlchemyRepository(db_session=db_session)
    with pytest.raises(EntityNotFoundException):
        repository.get_by_id(Person.next_id())


@pytest.mark.integration
def test_sqlalchemy_repository_remove_by_id_raises_exception(db_session):
    repository = PersonSqlAlchemyRepository(db_session=db_session)
    with pytest.raises(EntityNotFoundException):
        repository.remove_by_id(Person.next_id())
