from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from seedwork.domain.entities import Entity, GenericUUID

MapperEntity = TypeVar("MapperEntity", bound=Entity)
MapperModel = TypeVar("MapperModel", bound=Any)


class DataMapper(Generic[MapperEntity, MapperModel], ABC):
    entity_class: type[MapperEntity]
    model_class: type[MapperModel]

    @abstractmethod
    def model_to_entity(self, instance: MapperModel) -> MapperEntity:
        raise NotImplementedError()

    @abstractmethod
    def entity_to_model(self, entity: MapperEntity) -> MapperModel:
        raise NotImplementedError()


class JSONDataMapper(DataMapper):
    def model_to_entity(self, instance: MapperModel) -> MapperEntity:
        entity_id = GenericUUID(instance.get("id"))
        entity_dict = {
            "id": entity_id,
            **instance["data"],
        }
        return self.entity_class(**entity_dict)

    def entity_to_model(self, entity: MapperEntity) -> MapperModel:
        data = dict(**entity.__dict__)
        entity_id = str(data.pop("id"))
        return self.model_class(
            **{
                "id": entity_id,
                "data": data,
            }
        )
