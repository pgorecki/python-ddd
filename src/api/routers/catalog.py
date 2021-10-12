from fastapi import APIRouter, Depends
from seedwork.infrastructure.request_context import request_context

from modules.catalog.module import CatalogModule
from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
)
from modules.catalog.application.query.get_all_listings import GetAllListings
from modules.catalog.application.query.get_listing_details import GetListingDetails


from config.container import Container, inject

router = APIRouter()


def dependency(provider):
    from dependency_injector.wiring import Provide

    return Depends(Provide[provider])


@router.get("/catalog", tags=["catalog"])
@inject
async def get_all_listings(
    module: CatalogModule = dependency(Container.catalog_module),
):
    query_result = module.execute_query(GetAllListings())
    """
    Shows all published listings in the catalog
    """
    return {"data": query_result.result}


@router.get("/catalog/add_next", tags=["catalog"])
@inject
async def get_listing_details(
    module: CatalogModule = dependency(Container.catalog_module),
):
    """just for testing...."""
    from modules.catalog.infrastructure.listing_repository import CatalogListing

    count = module.listing_repository.count()
    listing = CatalogListing(
        id=module.listing_repository.next_id(), data=dict(name=f"foo-{count}")
    )
    module.listing_repository.session.add(listing)
    return {"data": count}


@router.get("/catalog/{listing_id}", tags=["catalog"])
@inject
async def get_listing_details(
    listing_id, module: CatalogModule = dependency(Container.catalog_module)
):
    """
    Shows listing details
    """
    query_result = module.execute_query(GetListingDetails(listing_id=listing_id))
    """
    Shows all published listings in the catalog
    """
    return {"data": query_result.result}

    return {"data": "catalog here"}


@router.post("/catalog", tags=["catalog"], status_code=201)
async def create_listing(module: CatalogModule = dependency(Container.catalog_module)):
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
