from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from modules.bidding.domain.rules import (
    BidCanBeRetracted,
    ListingCanBeCancelled,
    PlacedBidMustBeGreaterThanCurrentWinningBid,
)
from modules.bidding.domain.value_objects import Bid, Bidder, Seller
from seedwork.domain.entities import AggregateRoot
from seedwork.domain.events import DomainEvent
from seedwork.domain.exceptions import DomainException
from seedwork.domain.value_objects import Money


class BidderIsNotBiddingListing(DomainException):
    ...


class BidCannotBeRetracted(DomainException):
    ...


class ListingCannotBeCancelled(DomainException):
    ...


class BidPlacedEvent(DomainEvent):
    ...


class BidRetractedEvent(DomainEvent):
    ...


class ListingCancelledEvent(DomainEvent):
    ...


@dataclass(kw_only=True)
class Listing(AggregateRoot):
    seller: Seller
    initial_price: Money
    starts_at: datetime
    ends_at: datetime
    bids: list[Bid] = field(default_factory=list)

    @property
    def current_price(self) -> Money:
        highest_price = self.initial_price
        second_highest_price = self.initial_price

        if len(self.bids) == 1:
            return min(self.bids[0].max_price, self.initial_price)

        for bid in self.bids:
            if bid.max_price > highest_price:
                second_highest_price = highest_price
                highest_price = bid.max_price

        return second_highest_price + Money(1, currency=self.initial_price.currency)

    # public commands
    def place_bid(self, bid: Bid) -> type[DomainEvent]:
        """Public method"""
        self.check_rule(
            PlacedBidMustBeGreaterThanCurrentWinningBid(
                bid=bid, current_price=self.current_price
            )
        )

        if self.has_bid_placed_by(bidder=bid.bidder):
            self._update_bid(bid)
        else:
            self._add_bid(bid)

        return BidPlacedEvent(
            listing_id=self.id, bidder=bid.bidder, max_price=bid.max_price
        )

    def retract_bid_of(self, bidder: Bidder) -> type[DomainEvent]:
        """Public method"""
        bid = self.get_bid_of(bidder)
        self.check_rule(
            BidCanBeRetracted(listing_ends_at=self.ends_at, bid_placed_at=bid.placed_at)
        )

        self._remove_bid_of(bidder=bidder)
        return BidRetractedEvent(listing_id=self.id, bidder_id=bidder.uuid)

    def cancel(self) -> type[DomainEvent]:
        """
        Seller can cancel a listing (end a listing early). Listing must be eligible to cancelled,
        depending on time left and if bids have been placed.
        """
        self.check_rule(
            ListingCanBeCancelled(
                time_left_in_listing=self.time_left_in_listing,
                no_bids_were_placed=len(self.bids) == 0,
            )
        )
        self.ends_at = datetime.utcnow()
        return ListingCancelledEvent(listing_id=self.id)

    def end(self) -> type[DomainEvent]:
        """
        Ends listing.
        """
        raise NotImplementedError()
        return []

    # public queries
    def get_bid_of(self, bidder: Bidder) -> Bid:
        try:
            bid = next(filter(lambda bid: bid.bidder == bidder, self.bids))
        except StopIteration as e:
            raise BidderIsNotBiddingListing() from e
        return bid

    def has_bid_placed_by(self, bidder: Bidder) -> bool:
        """Checks if listing has a bid placed by a bidder"""
        try:
            self.get_bid_of(bidder=bidder)
        except BidderIsNotBiddingListing:
            return False
        return True

    @property
    def winning_bid(self) -> Optional[Bid]:
        try:
            highest_bid = max(self.bids, key=lambda bid: bid.max_price)
        except ValueError:
            # nobody is bidding
            return None
        return highest_bid

    @property
    def time_left_in_listing(self):
        now = datetime.utcnow()
        zero_seconds = timedelta()
        return max(self.ends_at - now, zero_seconds)

    # private commands and queries
    def _add_bid(self, bid: Bid):
        assert not self.has_bid_placed_by(
            bidder=bid.bidder
        ), "Only one bid of a bidder is allowed"
        self.bids.append(bid)

    def _update_bid(self, bid: Bid):
        self.bids = [
            bid if bid.bidder == existing.bidder else existing for existing in self.bids
        ]
