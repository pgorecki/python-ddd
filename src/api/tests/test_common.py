import pytest


@pytest.mark.integration
def test_homepage_returns_200(api_client):
    response = api_client.get("/")
    assert response.status_code == 200


@pytest.mark.integration
def test_docs_page_returns_200(api_client):
    response = api_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.integration
def test_openapi_schema_returns_200(api_client):
    response = api_client.get("/openapi.json")
    assert response.status_code == 200
