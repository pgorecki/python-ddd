from datetime import date
from typing import Any
from seedwork.domain.entities import Entity
from seedwork.domain.value_objects import Currency, UUID
from .rules import ListingPriceMustBeGreaterThanZero


class Listing(Entity):
    class ListingStatus:
        DRAFT = "draft"

    title: str
    description: str
    price: Currency
    seller_id: UUID
    status = ListingStatus.DRAFT

    def change_main_attributes(self, title: str, description: str, price: Currency):
        self.title = title
        self.description = description
        self.price = price
