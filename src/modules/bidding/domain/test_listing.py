from freezegun import freeze_time
import pytest
from datetime import datetime, timedelta
from modules.bidding.domain.entities import Seller, Listing, Money
from modules.bidding.domain.value_objects import Bidder, Bid
from seedwork.domain.value_objects import UUID
from seedwork.domain.exceptions import BusinessRuleValidationException


def test_listing_initial_price():
    seller = Seller(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    assert listing.winning_bid is None


def test_place_one_bid():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    bid = Bid(price=Money(20), bidder=bidder, placed_at=now)
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(bid)
    assert listing.winning_bid == Bid(Money(20), bidder=bidder, placed_at=now)


def test_place_two_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder1 = Bidder(id=UUID.v4())
    bidder2 = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(price=Money(20), bidder=bidder1, placed_at=now))
    listing.place_bid(Bid(price=Money(30), bidder=bidder2, placed_at=now))
    assert listing.winning_bid == Bid(Money(30), bidder=bidder2, placed_at=now)


def test_place_two_bids_by_same_bidder():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(price=Money(20), bidder=bidder, placed_at=now))
    listing.place_bid(Bid(price=Money(30), bidder=bidder, placed_at=now))

    assert len(listing.bids) == 1
    assert listing.winning_bid == Bid(price=Money(30), bidder=bidder, placed_at=now)


def test_cannot_place_bid_if_listing_ended():
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    bid = Bid(
        price=Money(10),
        bidder=bidder,
        placed_at=datetime.utcnow() + timedelta(seconds=1),
    )
    with pytest.raises(
        BusinessRuleValidationException,
        match="PlacedBidMustBeGreaterThanCurrentWinningBid",
    ):
        listing.place_bid(bid)


def test_retract_bid():
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.utcnow(),
    )
    bid = Bid(
        price=Money(100),
        bidder=bidder,
        placed_at=datetime.utcnow() - timedelta(seconds=1),
    )
    listing.place_bid(bid)
    with pytest.raises(BusinessRuleValidationException, match="BidCanBeRetracted"):
        listing.retract_bid_of(bidder=bidder)


def test_cancel_listing():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=now + timedelta(days=10),
    )

    listing.cancel_listing()

    assert listing.time_left_in_listing == timedelta()


def test_can_cancel_listing_with_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=now + timedelta(days=10),
    )
    bid = Bid(
        price=Money(100),
        bidder=bidder,
        placed_at=now,
    )
    listing.place_bid(bid)

    listing.cancel_listing()

    assert listing.time_left_in_listing == timedelta()


def test_cannot_cancel_listing_with_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=now + timedelta(hours=1),
    )
    bid = Bid(
        price=Money(100),
        bidder=bidder,
        placed_at=now,
    )
    listing.place_bid(bid)

    with pytest.raises(BusinessRuleValidationException, match="ListingCanBeCancelled"):
        listing.cancel_listing()
