from datetime import datetime, timedelta

import pytest

from modules.bidding.domain.entities import Listing, Money, Seller
from modules.bidding.domain.value_objects import Bid, Bidder
from seedwork.domain.exceptions import BusinessRuleValidationException
from seedwork.domain.value_objects import UUID


@pytest.mark.unit
def test_listing_initial_price():
    seller = Seller(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    assert listing.winning_bid is None


@pytest.mark.unit
def test_place_one_bid():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    bid = Bid(max_price=Money(20), bidder=bidder, placed_at=now)
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(bid)
    assert listing.winning_bid == Bid(Money(20), bidder=bidder, placed_at=now)
    assert listing.current_price == Money(10)


@pytest.mark.unit
def test_place_two_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder1 = Bidder(id=UUID.v4())
    bidder2 = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(max_price=Money(15), bidder=bidder1, placed_at=now))
    listing.place_bid(Bid(max_price=Money(30), bidder=bidder2, placed_at=now))
    assert listing.winning_bid == Bid(Money(30), bidder=bidder2, placed_at=now)
    assert listing.current_price == Money(16)


@pytest.mark.unit
def test_place_two_bids_by_same_bidder():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(max_price=Money(20), bidder=bidder, placed_at=now))
    listing.place_bid(Bid(max_price=Money(30), bidder=bidder, placed_at=now))

    assert len(listing.bids) == 1
    assert listing.winning_bid == Bid(max_price=Money(30), bidder=bidder, placed_at=now)
    assert listing.current_price == Money(10)


@pytest.mark.unit
def test_cannot_place_bid_if_listing_ended():
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    bid = Bid(
        max_price=Money(10),
        bidder=bidder,
        placed_at=datetime.utcnow() + timedelta(seconds=1),
    )
    with pytest.raises(
        BusinessRuleValidationException,
        match="PlacedBidMustBeGreaterThanCurrentWinningBid",
    ):
        listing.place_bid(bid)


@pytest.mark.unit
def test_retract_bid():
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    bid = Bid(
        max_price=Money(100),
        bidder=bidder,
        placed_at=datetime.utcnow() - timedelta(seconds=1),
    )
    listing.place_bid(bid)
    with pytest.raises(BusinessRuleValidationException, match="BidCanBeRetracted"):
        listing.retract_bid_of(bidder=bidder)


@pytest.mark.unit
def test_cancel_listing():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=now,
        ends_at=now + timedelta(days=10),
    )

    listing.cancel()

    assert listing.time_left_in_listing == timedelta()


@pytest.mark.unit
def test_can_cancel_listing_with_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=now,
        ends_at=now + timedelta(days=10),
    )
    bid = Bid(
        max_price=Money(100),
        bidder=bidder,
        placed_at=now,
    )
    listing.place_bid(bid)

    listing.cancel()

    assert listing.time_left_in_listing == timedelta()


@pytest.mark.unit
def test_cannot_cancel_listing_with_bids():
    now = datetime.utcnow()
    seller = Seller(id=UUID.v4())
    bidder = Bidder(id=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        starts_at=now,
        ends_at=now + timedelta(hours=1),
    )
    bid = Bid(
        max_price=Money(100),
        bidder=bidder,
        placed_at=now,
    )
    listing.place_bid(bid)

    with pytest.raises(BusinessRuleValidationException, match="ListingCanBeCancelled"):
        listing.cancel()
