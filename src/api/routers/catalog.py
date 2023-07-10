import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies import Application, User, get_application, get_authenticated_user
from api.models.catalog import ListingIndexModel, ListingReadModel, ListingWriteModel
from config.container import inject
from modules.catalog.application.command import (
    CreateListingDraftCommand,
    DeleteListingDraftCommand,
    PublishListingDraftCommand,
)
from modules.catalog.application.query.get_all_listings import GetAllListings
from modules.catalog.application.query.get_listing_details import GetListingDetails
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
    current_user: Annotated[User, Depends(get_authenticated_user)],
):
    """
    Creates a new listing.
    """
    command = CreateListingDraftCommand(
        listing_id=uuid.uuid4(),
        title=request_body.title,
        description=request_body.description,
        ask_price=Money(request_body.ask_price_amount, request_body.ask_price_currency),
        seller_id=current_user.id,
    )
    app.execute_command(command)

    query = GetListingDetails(listing_id=command.listing_id)
    query_result = app.execute_query(query)
    return dict(query_result.payload)


@router.delete(
    "/catalog/{listing_id}", tags=["catalog"], status_code=204, response_model=None
)
@inject
async def delete_listing(
    listing_id,
    app: Annotated[Application, Depends(get_application)],
    current_user: Annotated[User, Depends(get_authenticated_user)],
):
    """
    Delete listing
    """
    command = DeleteListingDraftCommand(
        listing_id=listing_id,
        seller_id=current_user.id,
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
