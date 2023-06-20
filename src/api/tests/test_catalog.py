import pytest

from modules.catalog.application.command import (
    CreateListingDraftCommand,
    PublishListingDraftCommand,
)
from seedwork.domain.value_objects import UUID, Money


@pytest.mark.integration
def test_empty_catalog_list(api_client):
    response = api_client.get("/catalog")
    assert response.status_code == 200
    assert response.json() == {"data": []}


@pytest.mark.integration
def test_catalog_list_with_one_item(app, api_client):
    # arrange
    command_result = app.execute_command(
        CreateListingDraftCommand(
            listing_id=UUID(int=1),
            title="Foo",
            description="Bar",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )

    # act
    response = api_client.get("/catalog")

    # assert
    assert response.status_code == 200
    response_data = response.json()["data"]
    assert len(response_data) == 1
    assert response.json() == {
        "data": [
            {
                "id": str(UUID(int=1)),
                "title": "Foo",
                "description": "Bar",
                "ask_price_amount": 10.0,
                "ask_price_currency": "USD",
            }
        ]
    }


@pytest.mark.integration
def test_catalog_list_with_two_items(app, api_client):
    # arrange
    app.execute_command(
        CreateListingDraftCommand(
            listing_id=UUID(int=1),
            title="Foo #1",
            description="Bar",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )
    app.execute_command(
        CreateListingDraftCommand(
            listing_id=UUID(int=2),
            title="Foo #2",
            description="Bar",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )

    # act
    response = api_client.get("/catalog")

    # assert
    assert response.status_code == 200
    response_data = response.json()["data"]
    assert len(response_data) == 2


def test_catalog_create_draft_fails_due_to_incomplete_data(api, api_client):
    response = api_client.post("/catalog")
    assert response.status_code == 422


@pytest.mark.integration
def test_catalog_delete_draft(app, api_client):
    app.execute_command(
        CreateListingDraftCommand(
            listing_id=UUID(int=1),
            title="Listing to be deleted",
            description="...",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )

    response = api_client.delete(f"/catalog/{str(UUID(int=1))}")

    assert response.status_code == 204


@pytest.mark.integration
def test_catalog_delete_non_existing_draft_returns_404(api_client):
    listing_id = UUID("00000000000000000000000000000001")
    response = api_client.delete(f"/catalog/{listing_id}")
    assert response.status_code == 404


@pytest.mark.integration
def test_catalog_publish_listing_draft(app, api_client):
    # arrange
    listing_id = UUID(int=1)
    app.execute_command(
        CreateListingDraftCommand(
            listing_id=listing_id,
            title="Listing to be published",
            description="...",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )

    # act
    response = api_client.post(f"/catalog/{listing_id}/publish")

    # assert that the listing was published
    assert response.status_code == 200


def test_published_listing_appears_in_biddings(app, api_client):
    # arrange
    listing_id = UUID(int=1)
    app.execute_command(
        CreateListingDraftCommand(
            listing_id=listing_id,
            title="Listing to be published",
            description="...",
            ask_price=Money(10),
            seller_id=UUID("00000000000000000000000000000002"),
        )
    )
    app.execute_command(
        PublishListingDraftCommand(
            listing_id=listing_id,
        )
    )

    url = f"/bidding/{listing_id}"
    response = api_client.get(url)
    assert response.status_code == 200
