from seedwork.domain.entities import Entity
from seedwork.application.exceptions import EntityNotFoundException


class Repository:
    pass


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.objects = {}

    def get_by_id(self, id) -> Entity:
        try:
            return self.objects[id]
        except KeyError:
            raise EntityNotFoundException

    def insert(self, entity: Entity):
        assert issubclass(entity.__class__, Entity)
        self.objects[entity.id] = entity

    def update(self, entity: Entity):
        assert issubclass(entity.__class__, Entity)
        self.objects[entity.id] = entity

    def delete(self, entity_id):
        del self.objects[entity_id]

    def __len__(self):
        return len(self.objects)
