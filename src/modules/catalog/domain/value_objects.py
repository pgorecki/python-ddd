from seedwork.domain.value_objects import GenericUUID, ValueObject

# some aliases to fight primitive obsession
ListingId = GenericUUID
SellerId = GenericUUID


class ListingStatus(ValueObject):
    DRAFT = "draft"
    PUBLISHED = "published"
