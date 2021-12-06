from seedwork.domain.rules import BusinessRule
from modules.bidding.domain.value_objects import Bid
from seedwork.domain.value_objects import Money


class PlacedBidMustBeGreaterThanCurrentWinningBid(BusinessRule):
    __message = "Placed bid must be greater than {current_price}"

    bid: Bid
    current_price: Money

    def is_broken(self) -> bool:
        return self.bid.price <= self.current_price

    def get_message(self) -> str:
        return self.__message.format(current_price=self.current_price)
