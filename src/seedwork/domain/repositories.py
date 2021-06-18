from .entities import Entity
from .value_objects import UUID


class GenericRepository:
    def get_by_id(self, id: UUID) -> Entity:
        pass

    def insert(self, entity: Entity):
        pass

    def update(self, entity: Entity):
        pass

    def delete(self, entity_id: UUID):
        pass
