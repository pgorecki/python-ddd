from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from modules.bidding.domain.events import (
    BidWasPlaced,
    BidWasRetracted,
    HighestBidderWasOutbid,
    ListingWasCancelled,
)
from modules.bidding.domain.rules import (
    BidCanBeRetracted,
    ListingCanBeCancelled,
    PriceOfPlacedBidMustBeGreaterOrEqualThanNextMinimumPrice,
)
from modules.bidding.domain.value_objects import Bid, Bidder, Seller
from seedwork.domain.entities import AggregateRoot
from seedwork.domain.events import DomainEvent
from seedwork.domain.exceptions import DomainException
from seedwork.domain.value_objects import GenericUUID, Money


class BidderIsNotBiddingListing(DomainException):
    ...


class BidCannotBeRetracted(DomainException):
    ...


class ListingCannotBeCancelled(DomainException):
    ...


@dataclass(kw_only=True)
class Listing(AggregateRoot[GenericUUID]):
    seller: Seller
    ask_price: Money
    starts_at: datetime
    ends_at: datetime
    bids: list[Bid] = field(default_factory=list)

    # public queries
    @property
    def current_price(self) -> Money:
        """The current price is the price buyers are competing against"""
        if len(self.bids) < 2:
            return self.ask_price

        sorted_prices = sorted([bid.max_price for bid in self.bids], reverse=True)
        return sorted_prices[1]

    @property
    def next_minimum_price(self) -> Money:
        return self.current_price + Money(1, currency=self.ask_price.currency)

    # public commands
    def place_bid(self, bid: Bid):
        """Public method"""
        self.check_rule(
            PriceOfPlacedBidMustBeGreaterOrEqualThanNextMinimumPrice(
                current_price=bid.max_price, next_minimum_price=self.next_minimum_price
            )
        )

        previous_winner_id = self.highest_bid.bidder.id if self.highest_bid else None
        current_winner_id = bid.bidder.id

        if self.has_bid_placed_by(bidder=bid.bidder):
            self._update_bid(bid)
        else:
            self._add_bid(bid)

        self.register_event(
            BidWasPlaced(
                listing_id=self.id,
                bidder_id=bid.bidder.id,
            )
        )

        # if there was previous winner...
        if previous_winner_id is not None and previous_winner_id != current_winner_id:
            self.register_event(
                HighestBidderWasOutbid(
                    listing_id=self.id,
                    outbid_bidder_id=previous_winner_id,
                )
            )

    def retract_bid_of(self, bidder: Bidder):
        """Public method"""
        bid = self.get_bid_of(bidder)
        self.check_rule(
            BidCanBeRetracted(listing_ends_at=self.ends_at, bid_placed_at=bid.placed_at)
        )

        self._remove_bid_of(bidder=bidder)
        self.register_event(
            BidWasRetracted(
                listing_id=self.id,
                retracting_bidder_id=bidder.id,
                winning_bidder_id=self.highest_bid.bidder.id
                if self.highest_bid
                else None,
            )
        )

    def cancel(self):
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
        self.register_event(ListingWasCancelled(listing_id=self.id))

    def end(self) -> DomainEvent:
        """
        Ends listing.
        """
        raise NotImplementedError()

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
    def highest_bid(self) -> Optional[Bid]:
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

    def _remove_bid_of(self, bidder: Bidder):
        self.bids = [bid for bid in self.bids if bid.bidder != bidder]
