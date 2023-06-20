import pytest


@pytest.mark.integration
def test_debug_endpoint(api_client):
    response = api_client.get("/debug")
    assert response.status_code == 200
