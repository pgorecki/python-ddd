from pydantic import BaseModel, Field
from .value_objects import UUID


class Entity(BaseModel):
    id: UUID = Field(default_factory=UUID.v4)
