from seedwork.domain.value_objects import ValueObject


class ListingStatus(ValueObject):
    DRAFT = "draft"
    PUBLISHED = "published"
