import pytest
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.command_handlers import create_listing_draft
from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.domain.value_objects import UUID


def test_create_listing_draft():
    # arrange
    command = CreateListingDraftCommand(
        title="foo", description="bar", price=1, seller_id=UUID.v4()
    )
    repository = InMemoryRepository()

    # act
    result = create_listing_draft(command, repository)

    # assert
    assert repository.get_by_id(result.id).title == "foo"
    assert result.has_errors() is False
