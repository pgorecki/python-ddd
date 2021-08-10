from seedwork.application.commands import Command
from seedwork.domain.value_objects import Currency, UUID


class CreateListingDraftCommand(Command):
    """A command for creating new listing in draft state"""

    title: str
    description: str
    price: Currency
    seller_id: UUID


class UpdateListingDraftCommand(Command):
    """A command for updating a listing"""

    listing_id: UUID
    title: str
    description: str
    price: Currency
    modify_user_id: UUID


class PublishListingCommand(Command):
    """A command for publishing a listing in draft state"""

    listing_id: UUID
    seller_id: UUID
