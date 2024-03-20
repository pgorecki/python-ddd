from seedwork.domain.value_objects import GenericUUID, ValueObject
from enum import Enum

# some aliases to fight primitive obsession
ListingId = GenericUUID
SellerId = GenericUUID


class ListingStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
