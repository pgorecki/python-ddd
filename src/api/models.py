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
    description: str
    ask_price_amount: float
    ask_price_currency: str = "USD"


class ListingReadModel(BaseModel):
    id: UUID
    title: str = ""
    description: str
    ask_price_amount: float
    ask_price_currency: str


class ListingIndexModel(BaseModel):
    data: list[ListingReadModel]
