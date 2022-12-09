from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_homepage_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_docs_page_returns_200():
    response = client.get("/docs")
    assert response.status_code == 200
