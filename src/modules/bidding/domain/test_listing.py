from modules.bidding.domain.entities import Seller, Listing, Money
from modules.bidding.domain.value_objects import Bidder, Bid
from seedwork.domain.value_objects import UUID


def test_listing_initial_price():
    seller = Seller(uuid=UUID.v4())
    listing = Listing(id=Listing.next_id(), seller=seller, initial_price=Money(10))
    assert listing.winning_bid == None


def test_place_one_bid():
    seller = Seller(uuid=UUID.v4())
    bidder = Bidder(uuid=UUID.v4())
    bid = Bid(price=Money(20), bidder=bidder)
    listing = Listing(id=Listing.next_id(), seller=seller, initial_price=Money(10))
    listing.place_bid(bid)
    assert listing.winning_bid == Bid(Money(10), bidder=bidder)


def test_place_two_bids():
    seller = Seller(uuid=UUID.v4())
    bidder1 = Bidder(uuid=UUID.v4())
    bid1 = Bid(price=Money(20), bidder=bidder1)
    bidder2 = Bidder(uuid=UUID.v4())
    bid2 = Bid(price=Money(30), bidder=bidder2)
    listing = Listing(id=Listing.next_id(), seller=seller, initial_price=Money(10))
    listing.place_bid(bid1)
    listing.place_bid(bid2)
    assert listing.winning_bid == Bid(Money(30), bidder=bidder2)

    """
    Here's an example:

The current bid for an item is $10.00. Tom is the high bidder, and has placed a maximum bid of $12.00 on the item. His maximum bid is kept confidential from other members.

Laura views the item and places a maximum bid of $15.00. Laura becomes the high bidder.

Tom's bid is raised to his maximum of $12.00. Laura's bid is now $12.50.

We send Tom an email that he has been outbid. If he doesn't raise his maximum bid, Laura wins the item.
    """
