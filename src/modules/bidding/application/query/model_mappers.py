from datetime import datetime

from pydantic import BaseModel

from modules.bidding.infrastructure.listing_repository import ListingModel
from seedwork.domain.value_objects import GenericUUID


class ListingDAO(BaseModel):
    id: GenericUUID
    ends_at: datetime
    bids: list


def map_listing_model_to_dao(instance: ListingModel):
    """maps ListingModel to a data access object (a dictionary)"""
    data = instance.data
    return ListingDAO(
        id=instance.id,
        ends_at=data["ends_at"],
        bids=[],
    )
