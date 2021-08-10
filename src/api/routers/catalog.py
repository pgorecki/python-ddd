from fastapi import APIRouter, Depends
from seedwork.domain.value_objects import UUID

from modules.catalog.module import CatalogModule
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.queries import GetAllListingsQuery

from ..dependencies import request_context, RequestContext
from ..modules import catalog_module as module


router = APIRouter()


@router.get("/catalog", tags=["catalog"])
async def get_all_listings():
    result = module.execute_query(GetAllListingsQuery())
    """
    Shows all published listings in the catalog
    """
    return {"data": result}


@router.get("/catalog/{listing_id}", tags=["catalog"])
async def get_listing_details(listing_id: UUID):
    """
    Shows all published listings in the catalog
    """
    return {"message": "catalog here"}


@router.post("/catalog", tags=["catalog"], status_code=201)
async def create_listing(request_context: RequestContext = Depends(request_context)):
    """
    Creates a new listing.
    """
    result = module.execute_command(
        CreateListingDraftCommand(
            title="title",
            description="",
            price=1,
            seller_id=request_context.current_user.id,
        )
    )
    # TODO: for now we return just the id, but in the future we should return
    # a representation of a newly created listing resource
    return {"id": result.id}
