from fastapi import APIRouter
from seedwork.domain.value_objects import UUID

router = APIRouter()


@router.get("/catalog", tags=["catalog"])
async def get_all_listings():
    """
    Shows all published listings in the catalog
    """
    return {"message": "catalog here"}


@router.get("/catalog/{listing_id}", tags=["catalog"])
async def get_listing_details(listing_id: UUID):
    """
    Shows all published listings in the catalog
    """
    return {"message": "catalog here"}


@router.post("/catalog", tags=["catalog"])
async def create_listing():
    """
    Creates a new listing.
    """
