from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: UUID
    username: str

    @classmethod
    def fake_user(cls):
        return CurrentUser(id=uuid4(), username="fake_user")


class ListingWriteModel(BaseModel):
    title: str


class ListingReadModel(BaseModel):
    id: UUID
    title: str = ""


class ListingIndexModel(BaseModel):
    data: List[ListingReadModel]
