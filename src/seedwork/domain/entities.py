from pydantic import BaseModel, Field
from .value_objects import UUID
from .mixins import BusinessRuleValidationMixin


class Entity(BusinessRuleValidationMixin, BaseModel):
    id: UUID = Field(default_factory=UUID.v4)
