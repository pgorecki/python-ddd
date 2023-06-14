from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BidReadModel(BaseModel):
    amount: float
    currency: str
    bidder_id: UUID
    bidder_username: str


class BiddingResponse(BaseModel):
    listing_id: UUID
    auction_status: str = "active"  # active, ended
    auction_end_date: datetime
    bids: list[BidReadModel]


class PlaceBidRequest(BaseModel):
    bidder_id: UUID
    amount: float
