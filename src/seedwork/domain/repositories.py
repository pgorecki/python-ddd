from abc import ABCMeta, abstractmethod
from .entities import Entity
from .value_objects import UUID


class GenericRepository(metaclass=ABCMeta):
    """An interface for a generic repository with CRUD operations"""

    @abstractmethod
    def get_by_id(self, id: UUID) -> Entity:
        ...

    @abstractmethod
    def insert(self, entity: Entity):
        ...

    @abstractmethod
    def update(self, entity: Entity):
        ...

    @abstractmethod
    def delete(self, entity_id: UUID):
        ...

    @staticmethod
    def next_id() -> UUID:
        return UUID.v4()
