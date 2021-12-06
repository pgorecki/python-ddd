from dataclasses import dataclass, field
from typing import List
from collections.abc import Sequence
from modules.bidding.domain.value_objects import Bid, Bidder, Seller
from modules.bidding.domain.rules import PlacedBidMustBeGreaterThanCurrentWinningBid
from seedwork.domain.entities import AggregateRoot
from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import UUID, Money


@dataclass(kw_only=True)
class Listing(AggregateRoot):
    seller: Seller
    initial_price: Money
    bids: List[Bid] = field(default_factory=list)
    current_price: Money = field(init=False)

    def __post_init__(self) -> None:
        self.current_price = self.initial_price

    def place_bid(self, bid: Bid) -> Sequence[DomainEvent]:
        self.check_rule(
            PlacedBidMustBeGreaterThanCurrentWinningBid(
                bid=bid, current_price=self.current_price
            )
        )
        self.bids.append(bid)
        return []

    def retract_bid(self) -> Sequence[DomainEvent]:
        return []

    def cancel_listing(self) -> Sequence[DomainEvent]:
        return []

    def end_bidding(self) -> Sequence[DomainEvent]:
        return []

    @property
    def winning_bid(self):
        return Bid(price=Money(0), bidder=Bidder(uuid=self.seller.uuid))
