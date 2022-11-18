import uuid

from seedwork.domain.entities import Entity


class JSONDataMapper:
    entity_class = None
    model_class = None

    def map_model_to_entity(self, instance) -> type[Entity]:
        entity_id = uuid.UUID(instance.get("id"))
        entity_dict = {
            "id": entity_id,
            **instance["data"],
        }
        return self.entity_class(**entity_dict)

    def map_entity_to_model(self, entity: type[Entity]):
        data = dict(**entity.__dict__)
        entity_id = str(data.pop("id"))
        return self.model_class(
            **{
                "id": entity_id,
                "data": data,
            }
        )
