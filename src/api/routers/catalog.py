from fastapi import APIRouter

from api.models import ListingIndexModel, ListingReadModel, ListingWriteModel
from api.shared import dependency
from config.container import Container, inject
from modules.catalog import CatalogModule
from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
)
from modules.catalog.application.query.get_all_listings import GetAllListings
from modules.catalog.application.query.get_listing_details import GetListingDetails
from seedwork.domain.value_objects import Money
from seedwork.infrastructure.request_context import request_context

router = APIRouter()


@router.get("/catalog", tags=["catalog"], response_model=ListingIndexModel)
@inject
async def get_all_listings(
    module: CatalogModule = dependency(Container.catalog_module),
):
    """
    Shows all published listings in the catalog
    """
    query = GetAllListings()
    with module.unit_of_work():
        query_result = module.execute_query(query)
        return dict(data=query_result.payload)


@router.get("/catalog/{listing_id}", tags=["catalog"], response_model=ListingReadModel)
@inject
async def get_listing_details(
    listing_id,
    module: CatalogModule = dependency(Container.catalog_module),
):
    """
    Shows listing details
    """
    query = GetListingDetails(listing_id=listing_id)
    with module.unit_of_work():
        query_result = module.execute_query(query)
        return query_result.payload


@router.post(
    "/catalog", tags=["catalog"], status_code=201, response_model=ListingReadModel
)
@inject
async def create_listing(
    request_body: ListingWriteModel,
    module: CatalogModule = dependency(Container.catalog_module),
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
    with module.unit_of_work():
        command_result = module.execute_command(command)

        query = GetListingDetails(listing_id=command_result.result)
        query_result = module.execute_query(query)
        return query_result.payload


#
#     # TODO: for now we return just the id, but in the future we should return
#     # a representation of a newly created listing resource
#     return {"id": result.id}
