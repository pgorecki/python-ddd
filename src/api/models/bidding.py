from datetime import datetime

from pydantic import BaseModel

from seedwork.domain.value_objects import GenericUUID


class BidReadModel(BaseModel):
    amount: float
    currency: str
    bidder_id: GenericUUID
    bidder_username: str


class BiddingResponse(BaseModel):
    listing_id: GenericUUID
    auction_status: str = "active"  # active, ended
    auction_end_date: datetime
    bids: list[BidReadModel]


class PlaceBidRequest(BaseModel):
    bidder_id: GenericUUID
    amount: float
