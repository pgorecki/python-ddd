from fastapi import APIRouter

from api.models.bidding import BiddingReadModel
from api.shared import dependency
from config.container import Container, inject
from modules.bidding.application.query.get_bidding_details import GetBiddingDetails
from seedwork.application import Application

router = APIRouter()

"""
Inspired by https://developer.ebay.com/api-docs/buy/offer/types/api:Bidding
"""


@router.get("/bidding/{listing_id}", tags=["bidding"], response_model=BiddingReadModel)
@inject
async def get_bidding_details_of_listing(
    listing_id,
    app: Application = dependency(Container.application),
):
    """
    Shows listing details
    """
    query = GetBiddingDetails(listing_id=listing_id)
    query_result = app.execute_query(query)
    payload = query_result.payload
    return BiddingReadModel(
        listing_id=str(payload.id),
        auction_end_date=payload.ends_at,
        bids=payload.bids,
    )
