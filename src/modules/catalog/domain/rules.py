from seedwork.domain.rules import BusinessRule
from seedwork.domain.value_objects import Currency


class AuctionItemPriceMustBeGreaterThanZero(BusinessRule):
    message = "Price must be greater that zero"
    price: Currency

    def is_broken(self) -> bool:
        return self.price <= 0
