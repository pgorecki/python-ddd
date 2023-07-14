from abc import ABC

from modules.bidding.domain.entities import GenericUUID, Listing
from seedwork.domain.repositories import GenericRepository


class ListingRepository(GenericRepository[GenericUUID, Listing], ABC):
    """An interface for Listing repository"""
