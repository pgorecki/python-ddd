from seedwork.domain.aggregates import Aggregate
from seedwork.domain.value_objects import UUID

from modules.catalog.domain.repositories import ListingRepository


class MongoListingRepository(ListingRepository):
    def get_by_id(self, id: UUID) -> Aggregate:
        ...

    def get_by_id(self, id: UUID) -> Aggregate:
        ...

    def insert(self, entity: Aggregate):
        ...

    def update(self, entity: Aggregate):
        ...

    def delete(self, entity_id: UUID):
        ...
