import pytest
from datetime import datetime, timedelta
from modules.bidding.domain.entities import Seller, Listing, Money
from modules.bidding.domain.value_objects import Bidder, Bid
from seedwork.domain.value_objects import UUID
from seedwork.domain.exceptions import BusinessRuleValidationException


def test_listing_initial_price():
    seller = Seller(uuid=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    assert listing.winning_bid == None


def test_place_one_bid():
    now = datetime.utcnow()
    seller = Seller(uuid=UUID.v4())
    bidder = Bidder(uuid=UUID.v4())
    bid = Bid(price=Money(20), bidder=bidder, placed_at=now)
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    listing.place_bid(bid)
    assert (
        listing.winning_bid == Bid(Money(20), bidder=bidder, placed_at=now)
    )


def test_place_two_bids():
    now = datetime.utcnow()
    seller = Seller(uuid=UUID.v4())
    bidder1 = Bidder(uuid=UUID.v4())
    bidder2 = Bidder(uuid=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    listing.place_bid(Bid(price=Money(20), bidder=bidder1, placed_at=now))
    listing.place_bid(Bid(price=Money(30), bidder=bidder2, placed_at=now))
    assert listing.winning_bid == Bid(Money(30), bidder=bidder2, placed_at=now)


def test_place_two_bids_by_same_bidder():
    now = datetime.utcnow()
    seller = Seller(uuid=UUID.v4())
    bidder = Bidder(uuid=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    listing.place_bid(Bid(price=Money(20), bidder=bidder, placed_at=now))
    listing.place_bid(Bid(price=Money(30), bidder=bidder, placed_at=now))

    assert len(listing.bids) == 1
    assert listing.winning_bid == Bid(price=Money(30), bidder=bidder, placed_at=now)


def test_cannot_place_bid_if_listing_ended():
    seller = Seller(uuid=UUID.v4())
    bidder = Bidder(uuid=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    bid = Bid(
        price=Money(10), bidder=bidder, placed_at=datetime.now() + timedelta(seconds=1)
    )
    with pytest.raises(BusinessRuleValidationException):
        listing.place_bid(bid)


def test_retract_bid():
    seller = Seller(uuid=UUID.v4())
    bidder = Bidder(uuid=UUID.v4())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        initial_price=Money(10),
        ends_at=datetime.now(),
    )
    bid = Bid(
        price=Money(100), bidder=bidder, placed_at=datetime.utcnow() - timedelta(seconds=1)
    )
    listing.place_bid(bid)
    with pytest.raises(BusinessRuleValidationException):
        listing.retract_bid_of(bidder=bidder)

    """
    Here's an example:

The current bid for an item is $10.00. Tom is the high bidder, and has placed a maximum bid of $12.00 on the item. His maximum bid is kept confidential from other members.

Laura views the item and places a maximum bid of $15.00. Laura becomes the high bidder.

Tom's bid is raised to his maximum of $12.00. Laura's bid is now $12.50.

We send Tom an email that he has been outbid. If he doesn't raise his maximum bid, Laura wins the item.
    """
