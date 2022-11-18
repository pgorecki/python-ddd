from seedwork.domain.value_objects import ValueObject, UUID

# some aliases to fight primitive obsession
ListingId = UUID
SellerId = UUID


class ListingStatus(ValueObject):
    DRAFT = "draft"
    PUBLISHED = "published"
