from modules.catalog.application.commands import (
    CreateAuctionItemCommand,
    UpdateAuctionItemCommand,
    DeleteAuctionItemCommand,
    PublishAuctionItemCommand,
    UnpublishAuctionItemCommand,
)
from modules.catalog.domain.entities import AuctionItem
from seedwork.application.commands import Command
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler

# @unit_of_work
@command_handler
def create_auction_item(command: CreateAuctionItemCommand, repository) -> CommandResult:
    item = AuctionItem(**command.dict())
    try:
        repository.insert(item)
    except:
        return CommandResult.fail("Failed to add item")
    return CommandResult.succed(id=item.id)


# @unit_of_work
# @command_handler
def update_auction_item(command: UpdateAuctionItemCommand, repository):
    item = repository.find_by_id(command.id)
    item.title = command.title
    item.description = command.description
    repository.update(item)


# @unit_of_work
# @command_handler
def delete_auction_item(command: DeleteAuctionItemCommand, repository):
    repository.delete(command.id)


def publish_in_catalog(command: PublishAuctionItemCommand):
    pass


def unpublish_from_catalog(command: UnpublishAuctionItemCommand):
    pass


def xyz_view(request):
    publish_in_catalog(request.POST["id"])
