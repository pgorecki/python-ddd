import pytest


@pytest.mark.integration
def test_debug_endpoint(authenticated_api_client):
    response = authenticated_api_client.get("/debug")
    assert response.status_code == 200
