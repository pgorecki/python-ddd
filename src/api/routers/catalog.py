from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies import Application, get_application
from api.models.catalog import ListingIndexModel, ListingReadModel, ListingWriteModel
from config.container import inject
from modules.catalog.application.command import (
    CreateListingDraftCommand,
    DeleteListingDraftCommand,
    PublishListingDraftCommand,
)
from modules.catalog.application.query.get_all_listings import GetAllListings
from modules.catalog.application.query.get_listing_details import GetListingDetails
from seedwork.application import Application
from seedwork.domain.value_objects import Money

"""
Inspired by https://developer.ebay.com/api-docs/sell/inventory/resources/offer/methods/createOffer
"""

router = APIRouter()


@router.get("/catalog", tags=["catalog"], response_model=ListingIndexModel)
@inject
async def get_all_listings(app: Annotated[Application, Depends(get_application)]):
    """
    Shows all published listings in the catalog
    """
    query = GetAllListings()
    query_result = app.execute_query(query)
    return dict(data=query_result.payload)


@router.get("/catalog/{listing_id}", tags=["catalog"], response_model=ListingReadModel)
@inject
async def get_listing_details(
    listing_id, app: Annotated[Application, Depends(get_application)]
):
    """
    Shows listing details
    """
    query = GetListingDetails(listing_id=listing_id)
    query_result = app.execute_query(query)
    return dict(data=query_result.payload)


@router.post(
    "/catalog", tags=["catalog"], status_code=201, response_model=ListingReadModel
)
@inject
async def create_listing(
    request_body: ListingWriteModel,
    app: Annotated[Application, Depends(get_application)],
):
    """
    Creates a new listing.
    """
    command = CreateListingDraftCommand(
        title=request_body.title,
        description=request_body.description,
        ask_price=Money(request_body.ask_price_amount, request_body.ask_price_currency),
        seller_id=request_context.current_user.id,
    )
    command_result = app.execute_command(command)

    query = GetListingDetails(listing_id=command_result.payload)
    query_result = app.execute_query(query)
    return dict(query_result.payload)


@router.delete(
    "/catalog/{listing_id}", tags=["catalog"], status_code=204, response_model=None
)
@inject
async def delete_listing(
    listing_id, app: Annotated[Application, Depends(get_application)]
):
    """
    Delete listing
    """
    command = DeleteListingDraftCommand(
        listing_id=listing_id,
    )
    app.execute_command(command)


@router.post(
    "/catalog/{listing_id}/publish",
    tags=["catalog"],
    status_code=200,
    response_model=ListingReadModel,
)
@inject
async def publish_listing(
    listing_id: UUID, app: Annotated[Application, Depends(get_application)]
):
    """
    Creates a new listing.
    """
    command = PublishListingDraftCommand(
        listing_id=listing_id,
    )
    app.execute_command(command)

    query = GetListingDetails(listing_id=listing_id)
    query_result = app.execute_query(query)
    return dict(query_result.payload)
