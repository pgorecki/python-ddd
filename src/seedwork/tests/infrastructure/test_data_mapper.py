from uuid import UUID
from dataclasses import dataclass
from seedwork.domain.entities import Entity
from seedwork.infrastructure.data_mapper import JSONDataMapper


@dataclass
class PersonEntity(Entity):
    """Person entity"""

    name: str


class PersonJSONDataMapper(JSONDataMapper):
    entity_class = PersonEntity
    model_class = dict


def test_data_mapper_maps_entity_to_json():
    mapper = PersonJSONDataMapper()
    entity_instance = PersonEntity(
        id=UUID("12345678123456781234567812345678"), name="Bob"
    )

    actual = mapper.map_entity_to_model(entity_instance)

    expected = {"id": "12345678-1234-5678-1234-567812345678", "data": {"name": "Bob"}}

    assert actual == expected


def test_data_mapper_maps_json_to_entity():
    mapper = PersonJSONDataMapper()
    model_instance = {
        "id": "12345678-1234-5678-1234-567812345678",
        "data": {"name": "Bob"},
    }

    actual = mapper.map_model_to_entity(model_instance)

    expected = PersonEntity(id=UUID("12345678123456781234567812345678"), name="Bob")

    assert actual == expected
