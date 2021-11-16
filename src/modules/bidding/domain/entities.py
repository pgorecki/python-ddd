from dataclasses import dataclass
from typing import Set
from .value_objects import Bid
from seedwork.domain.value_objects import UUID


@dataclass
class Listing:
  ...


@dataclass
class Buyer:
  id: UUID

  def place_bid(listing: Listing, bid: Bid):
    listing.add_bid()

@dataclass
class Seller:
  ...


