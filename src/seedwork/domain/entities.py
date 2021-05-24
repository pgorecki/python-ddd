from pydantic import BaseModel, Field
import uuid


class Entity(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
