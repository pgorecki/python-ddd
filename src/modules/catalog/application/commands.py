from seedwork.application.commands import Command
from seedwork.domain.value_objects import Currency


class CreateAuctionItemCommand(Command):
    title: str
    description: str
    price: Currency


class UpdateAuctionItemCommand(Command):
    title: str
    description: str


class DeleteAuctionItemCommand(Command):
    pass


class PublishAuctionItemCommand(Command):
    pass


class UnpublishAuctionItemCommand(Command):
    pass
