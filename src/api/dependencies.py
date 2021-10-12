from fastapi import Header, HTTPException
from pydantic import BaseModel
from dataclasses import dataclass
from seedwork.domain.value_objects import UUID


class CurrentUser(BaseModel):
    id: UUID
    username = "fake_current_user"
    email = "fake@email.com"
    is_admin = True
