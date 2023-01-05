import pytest

from modules.catalog.application.command import CreateListingDraftCommand
from seedwork.domain.value_objects import Money


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
                title="Foo", description="Bar", ask_price=Money(10), seller_id="abcd"
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
                title="Foo #1", description="Bar", ask_price=Money(10), seller_id="abcd"
            )
        )
        catalog_module.execute_command(
            CreateListingDraftCommand(
                title="Foo #2", description="Bar", ask_price=Money(10), seller_id="abcd"
            )
        )

    # act
    response = api_client.get("/catalog")

    # assert
    assert response.status_code == 200
    response_data = response.json()["data"]
    assert len(response_data) == 2
