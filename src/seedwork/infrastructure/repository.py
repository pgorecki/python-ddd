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

    def persist(self, entity: Entity):
        self.objects[entity.id] = entity
