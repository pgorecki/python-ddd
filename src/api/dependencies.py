from pydantic import BaseModel

from seedwork.domain.value_objects import UUID


class CurrentUser(BaseModel):
    id: UUID
    username = "fake_current_user"
    email = "fake@email.com"
    is_admin = True
