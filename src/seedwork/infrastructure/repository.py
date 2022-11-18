from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from seedwork.application.exceptions import EntityNotFoundException
from seedwork.domain.entities import Entity
from seedwork.domain.value_objects import UUID


class Repository(ABC):
    """Base class for all repositories"""

    @abstractmethod
    def add(self, entity: type[Entity]):
        ...

    @abstractmethod
    def remove(self, entity: type[Entity]):
        ...

    @abstractmethod
    def get_by_id(self, id: type[UUID]):
        ...

    @abstractmethod
    def count(self) -> int:
        ...

    def __getitem__(self, key):
        return self.get_by_id(key)


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.objects = {}

    def get_by_id(self, id: type[UUID]) -> type[Entity]:
        try:
            return self.objects[id]
        except KeyError:
            raise EntityNotFoundException

    def add(self, entity: type[Entity]):
        assert issubclass(entity.__class__, Entity)
        self.objects[entity.id] = entity

    def remove(self, entity: type[Entity]):
        del self.objects[entity.id]

    def count(self):
        return len(self.objects)


# a sentinel value for keeping track of entites removed from the repository
class Removed:
    def __repr__(self):
        return "<Removed entity>"

    def __str__(self):
        return "<Removed entity>"


REMOVED = Removed()


class SqlAlchemyGenericRepository(Repository):
    data_mapper = None
    model_class: type[Entity] = None

    def __init__(self, db_session: Session, identity_map=None):
        self._session = db_session
        self._identity_map = identity_map or dict()

    def add(self, entity: Entity):
        self._identity_map[entity.id] = entity
        instance = self.map_entity_to_model(entity)
        self._session.add(instance)

    def remove(self, entity: Entity):
        self._check_not_removed(entity)
        self._identity_map[entity.id] = REMOVED
        listing_model = self.session.query(self.get_model_class()).get(entity.id)
        self._session.delete(listing_model)

    def get_by_id(self, id: UUID):
        instance = self._session.query(self.get_model_class()).get(id)
        return self._get_entity(instance)

    def persist(self, entity: Entity):
        self._check_not_removed(entity)
        assert (
            entity.id in self._identity_map
        ), "Cannon persist entity which is unknown to the repo. Did you forget to call repo.add() for this entity?"
        instance = self.map_entity_to_model(entity)
        merged = self._session.merge(instance)
        self._session.add(merged)

    def persist_all(self):
        for entity in self._identity_map.values():
            if entity is not REMOVED:
                self.persist(entity)

    def count(self) -> int:
        return self._session.query(self.model_class).count()

    def map_entity_to_model(self, entity: Entity):
        assert self.data_mapper
        return self.data_mapper.entity_to_model(entity)

    def map_model_to_entity(self, intance) -> Entity:
        assert self.data_mapper
        return self.data_mapper.model_to_entity(intance)

    def get_model_class(self):
        assert self.model_class is not None
        return self.model_class

    def _get_entity(self, instance):
        if instance is None:
            return None
        entity = self.map_model_to_entity(instance)
        self._check_not_removed(entity)

        if entity.id in self._identity_map:
            return self._identity_map[entity.id]

        self._identity_map[entity.id] = entity
        return entity

    def _check_not_removed(self, entity):
        assert (
            self._identity_map.get(entity.id, None) is not REMOVED
        ), f"Entity {entity.id} already removed"
