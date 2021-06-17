import pytest
from modules.catalog.application.commands import CreateAuctionItemCommand
from modules.catalog.application.command_handlers import create_auction_item
from seedwork.infrastructure.repository import InMemoryRepository


def test_create_auction_item_happy_path():
    # arrange
    command = CreateAuctionItemCommand(title="foo", description="bar", price=1)
    repository = InMemoryRepository()

    # act
    result = create_auction_item(command, repository)

    # assert
    assert repository.get_by_id(result.id).title == "foo"
    assert result.has_errors() is False


def test_create_auction_item_business_rule_validation_fails():
    command = CreateAuctionItemCommand(title="", description="bar")
    repository = InMemoryRepository()

    # with pytest.raises(Exception)
    # act
    result = create_auction_item(command, repository)
    assert result.has_errors()
