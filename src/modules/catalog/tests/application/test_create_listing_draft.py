from uuid import UUID

import pytest

from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
    create_listing_draft,
)
from modules.catalog.domain.entities import Seller
from seedwork.domain.value_objects import Money
from seedwork.infrastructure.repository import InMemoryRepository


@pytest.mark.unit
def test_create_listing_draft():
    # arrange
    command = CreateListingDraftCommand(
        listing_id=UUID(int=1),
        title="foo",
        description="bar",
        ask_price=Money(1),
        seller_id=Seller.next_id(),
    )
    repository = InMemoryRepository()

    # act
    result = create_listing_draft(command, repository)

    # assert
    assert repository.get_by_id(result.entity_id).title == "foo"
    assert result.has_errors() is False
