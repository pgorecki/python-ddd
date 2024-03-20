from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_application
from api.models.bidding import BiddingResponse, PlaceBidRequest
from config.container import inject
from modules.bidding.application.command import PlaceBidCommand, RetractBidCommand
from modules.bidding.application.query.get_bidding_details import GetBiddingDetails
from lato import Application

router = APIRouter()

"""
Inspired by https://developer.ebay.com/api-docs/buy/offer/types/api:Bidding
"""


@router.get("/bidding/{listing_id}", tags=["bidding"], response_model=BiddingResponse)
@inject
async def get_bidding_details_of_listing(
    listing_id, app: Annotated[Application, Depends(get_application)]
):
    """
    Shows listing details
    """
    query = GetBiddingDetails(listing_id=listing_id)
    result = app.execute(query)
    return BiddingResponse(
        listing_id=result.id,
        auction_end_date=result.ends_at,
        bids=result.bids,
    )


@router.post(
    "/bidding/{listing_id}/place_bid", tags=["bidding"], response_model=BiddingResponse
)
@inject
async def place_bid(
    listing_id,
    request_body: PlaceBidRequest,
    app: Annotated[Application, Depends(get_application)],
):
    """
    Places a bid on a listing
    """
    # TODO: get bidder from current user

    command = PlaceBidCommand(
        listing_id=listing_id,
        bidder_id=request_body.bidder_id,
        amount=request_body.amount,
    )
    app.execute(command)

    query = GetBiddingDetails(listing_id=listing_id)
    result = app.execute(query)
    return BiddingResponse(
        listing_id=result.id,
        auction_end_date=result.ends_at,
        bids=result.bids,
    )


@router.post(
    "/bidding/{listing_id}/retract_bid",
    tags=["bidding"],
    response_model=BiddingResponse,
)
@inject
async def retract_bid(
    listing_id, app: Annotated[Application, Depends(get_application)]
):
    """
    Retracts a bid from a listing
    """
    command = RetractBidCommand(
        listing_id=listing_id,
        bidder_id="",
    )
    app.execute(command)

    query = GetBiddingDetails(listing_id=listing_id)
    query_result = app.execute_query(query)
    payload = query_result.payload
    return BiddingResponse(
        listing_id=str(payload.id),
        auction_end_date=payload.ends_at,
        bids=payload.bids,
    )
