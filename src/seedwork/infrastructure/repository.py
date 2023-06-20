from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from seedwork.domain.entities import Entity
from seedwork.domain.exceptions import EntityNotFoundException
from seedwork.domain.value_objects import UUID
from seedwork.infrastructure.logging import logger


class Repository(ABC):
    """Base class for all repositories"""

    @abstractmethod
    def add(self, entity: type[Entity]):
        ...

    @abstractmethod
    def remove(self, entity: type[Entity]):
        ...

    @abstractmethod
    def get_by_id(self, entity_id: type[UUID]):
        """Should raise EntityNotFoundException if not found"""
        ...

    @abstractmethod
    def remove_by_id(self, entity_id: type[UUID]):
        """Should raise EntityNotFoundException if not found"""
        ...

    @abstractmethod
    def count(self) -> int:
        ...

    def __getitem__(self, key):
        return self.get_by_id(key)

    def __delitem__(self, key):
        return self.remove_by_id(key)


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.objects = {}

    def get_by_id(self, entity_id: type[UUID]) -> type[Entity]:
        try:
            return self.objects[entity_id]
        except KeyError:
            raise EntityNotFoundException(repository=self, entity_id=entity_id)

    def remove_by_id(self, entity_id: type[UUID]) -> type[Entity]:
        try:
            del self.objects[entity_id]
        except KeyError:
            raise EntityNotFoundException(repository=self, entity_id=entity_id)

    def add(self, entity: type[Entity]):
        assert issubclass(entity.__class__, Entity)
        self.objects[entity.id] = entity
        logger.debug(f"Added {entity} to {self}")

    def remove(self, entity: type[Entity]):
        del self.objects[entity.id]

    def count(self):
        return len(self.objects)

    def persist(self, entity: type[Entity]):
        ...

    def persist_all(self):
        ...


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
        self._check_not_removed(entity.id)
        self._identity_map[entity.id] = REMOVED
        instance = self._session.query(self.get_model_class()).get(entity.id)
        self._session.delete(instance)

    def remove_by_id(self, entity_id: UUID):
        self._check_not_removed(entity_id)
        self._identity_map[entity_id] = REMOVED
        instance = self._session.query(self.get_model_class()).get(entity_id)
        if instance is None:
            raise EntityNotFoundException(repository=self, entity_id=entity_id)
        self._session.delete(instance)

    def get_by_id(self, entity_id: UUID):
        instance = self._session.query(self.get_model_class()).get(entity_id)
        if instance is None:
            raise EntityNotFoundException(repository=self, entity_id=entity_id)
        return self._get_entity(instance)

    def persist(self, entity: Entity):
        """
        Persists all the changes made to the entity.
        Basically, entity is mapped to a model instance using a data_mapper, and then added to sqlalchemy session.
        """
        self._check_not_removed(entity.id)
        assert (
            entity.id in self._identity_map
        ), "Cannon persist entity which is unknown to the repo. Did you forget to call repo.add() for this entity?"
        instance = self.map_entity_to_model(entity)
        merged = self._session.merge(instance)
        self._session.add(merged)

    def persist_all(self):
        """Persists all changes made to entities known to the repository (present in the identity map)."""
        for entity in self._identity_map.values():
            if entity is not REMOVED:
                self.persist(entity)

    def count(self) -> int:
        return self._session.query(self.model_class).count()

    def map_entity_to_model(self, entity: Entity):
        assert self.data_mapper, (
            f"No data_mapper attribute in {self.__class__.__name__}. "
            "Make sure to include `data_mapper = MyDataMapper()` in the class."
        )

        return self.data_mapper.entity_to_model(entity)

    def map_model_to_entity(self, instance) -> Entity:
        assert self.data_mapper
        return self.data_mapper.model_to_entity(instance)

    def get_model_class(self):
        assert self.model_class is not None, (
            f"No model_class attribute in in {self.__class__.__name__}. "
            "Make sure to include `model_class = MyModel` in the class."
        )
        return self.model_class

    def _get_entity(self, instance):
        if instance is None:
            return None
        entity = self.map_model_to_entity(instance)
        self._check_not_removed(entity.id)

        if entity.id in self._identity_map:
            return self._identity_map[entity.id]

        self._identity_map[entity.id] = entity
        return entity

    def _check_not_removed(self, entity_id):
        assert (
            self._identity_map.get(entity_id, None) is not REMOVED
        ), f"Entity {entity_id} already removed"
