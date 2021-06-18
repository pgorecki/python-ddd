from datetime import datetime

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.domain.value_objects import Currency, UUID


class CreateListingDraftCommand(Command):
    title: str
    description: str
    price: Currency
    seller_id: UUID


class UpdateListingDraftCommand(Command):
    listing_id: UUID
    title: str
    description: str
    price: Currency
    modify_user_id: UUID
