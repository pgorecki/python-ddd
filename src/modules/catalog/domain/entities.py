from typing import Any
from seedwork.domain.entities import Entity
from seedwork.domain.value_objects import Currency
from .rules import AuctionItemPriceMustBeGreaterThanZero


class AuctionItem(Entity):
    title: str
    description: str
    price: Currency

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.check_rule(AuctionItemPriceMustBeGreaterThanZero(self.price))
