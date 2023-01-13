import pytest

from modules.catalog.application.command import CreateListingDraftCommand
from seedwork.domain.value_objects import UUID, Money


@pytest.mark.integration
def test_empty_catalog_list(api_client):
    response = api_client.get("/catalog")
    assert response.status_code == 200
    assert response.json() == {"data": []}


@pytest.mark.integration
def test_catalog_list_with_one_item(api, api_client):
    # arrange
    catalog_module = api.container.catalog_module()
    with catalog_module.unit_of_work():
        command_result = catalog_module.execute_command(
            CreateListingDraftCommand(
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
                "id": str(command_result.entity_id),
                "title": "Foo",
                "description": "Bar",
                "ask_price_amount": 10.0,
                "ask_price_currency": "USD",
            }
        ]
    }


@pytest.mark.integration
def test_catalog_list_with_two_items(api, api_client):
    # arrange
    catalog_module = api.container.catalog_module()
    with catalog_module.unit_of_work():
        catalog_module.execute_command(
            CreateListingDraftCommand(
                title="Foo #1",
                description="Bar",
                ask_price=Money(10),
                seller_id=UUID("00000000000000000000000000000002"),
            )
        )
        catalog_module.execute_command(
            CreateListingDraftCommand(
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


@pytest.mark.integration
def test_catalog_delete_draft(api, api_client):
    catalog_module = api.container.catalog_module()
    with catalog_module.unit_of_work():
        result = catalog_module.execute_command(
            CreateListingDraftCommand(
                title="Foo to be deleted",
                description="Bar",
                ask_price=Money(10),
                seller_id=UUID("00000000000000000000000000000002"),
            )
        )

    response = api_client.delete(f"/catalog/{result.entity_id}")

    assert response.status_code == 204


@pytest.mark.integration
def test_catalog_delete_non_existing_draft_returns_404(api, api_client):
    listing_id = UUID("00000000000000000000000000000001")
    response = api_client.delete(f"/catalog/{listing_id}")
    assert response.status_code == 404
