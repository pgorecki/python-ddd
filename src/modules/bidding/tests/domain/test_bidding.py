from datetime import datetime, timedelta

import pytest

from modules.bidding.domain.entities import Listing
from modules.bidding.domain.value_objects import Bid, Bidder, Money, Seller
from seedwork.domain.exceptions import BusinessRuleValidationException
from seedwork.domain.value_objects import GenericUUID


@pytest.mark.unit
def test_listing_initial_price():
    seller = Seller(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    assert listing.highest_bid is None


@pytest.mark.unit
def test_place_one_bid():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    bid = Bid(max_price=Money(20), bidder=bidder, placed_at=now)
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(bid)
    assert listing.highest_bid == Bid(max_price=Money(20), bidder=bidder, placed_at=now)
    assert listing.current_price == Money(10)


@pytest.mark.unit
def test_place_two_bids_second_buyer_outbids():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID(int=1))
    bidder1 = Bidder(id=GenericUUID(int=2))
    bidder2 = Bidder(id=GenericUUID(int=3))
    listing = Listing(
        id=GenericUUID(int=4),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    assert listing.current_price == Money(10)
    assert listing.next_minimum_price == Money(11)

    # bidder1 places a bid
    listing.place_bid(Bid(bidder=bidder1, max_price=Money(15), placed_at=now))
    assert listing.current_price == Money(10)
    assert listing.next_minimum_price == Money(11)

    # bidder2 successfully outbids bidder1
    listing.place_bid(Bid(bidder=bidder2, max_price=Money(30), placed_at=now))
    assert listing.current_price == Money(15)
    assert listing.next_minimum_price == Money(16)
    assert listing.highest_bid == Bid(Money(30), bidder=bidder2, placed_at=now)


@pytest.mark.unit
def test_place_two_bids_second_buyer_fails_to_outbid():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID(int=1))
    bidder1 = Bidder(id=GenericUUID(int=2))
    bidder2 = Bidder(id=GenericUUID(int=3))
    listing = Listing(
        id=GenericUUID(int=4),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )

    # bidder1 places a bid
    listing.place_bid(Bid(bidder=bidder1, max_price=Money(30), placed_at=now))
    assert listing.current_price == Money(10)
    assert listing.next_minimum_price == Money(11)

    # bidder2 tries to outbid bidder1...
    listing.place_bid(Bid(bidder=bidder2, max_price=Money(20), placed_at=now))

    # ...but he fails. bidder1 is still a winner, but current price changes
    assert listing.highest_bid == Bid(Money(30), bidder=bidder1, placed_at=now)
    assert listing.current_price == Money(20)


@pytest.mark.unit
def test_place_two_bids_second_buyer_fails_to_outbid_with_same_amount():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID(int=1))
    bidder1 = Bidder(id=GenericUUID(int=2))
    bidder2 = Bidder(id=GenericUUID(int=3))
    listing = Listing(
        id=GenericUUID(int=4),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(bidder=bidder1, max_price=Money(30), placed_at=now))
    listing.place_bid(Bid(bidder=bidder2, max_price=Money(30), placed_at=now))
    assert listing.highest_bid == Bid(Money(30), bidder=bidder1, placed_at=now)
    assert listing.current_price == Money(30)


@pytest.mark.unit
def test_place_two_bids_by_same_bidder():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow(),
    )
    listing.place_bid(Bid(max_price=Money(20), bidder=bidder, placed_at=now))
    listing.place_bid(Bid(max_price=Money(30), bidder=bidder, placed_at=now))

    assert len(listing.bids) == 1
    assert listing.highest_bid == Bid(max_price=Money(30), bidder=bidder, placed_at=now)
    assert listing.current_price == Money(10)


@pytest.mark.unit
def test_cannot_place_bid_if_listing_ended():
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
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
        match="PriceOfPlacedBidMustBeGreaterOrEqualThanNextMinimumPrice",
    ):
        listing.place_bid(bid)


@pytest.mark.unit
def test_retract_bid():
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
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
    seller = Seller(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
        starts_at=now,
        ends_at=now + timedelta(days=10),
    )

    listing.cancel()

    assert listing.time_left_in_listing == timedelta()


@pytest.mark.unit
def test_can_cancel_listing_with_bids():
    now = datetime.utcnow()
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
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
    seller = Seller(id=GenericUUID.next_id())
    bidder = Bidder(id=GenericUUID.next_id())
    listing = Listing(
        id=Listing.next_id(),
        seller=seller,
        ask_price=Money(10),
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
