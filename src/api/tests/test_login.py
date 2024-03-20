import pytest

from modules.iam.application.services import IamService
from seedwork.domain.value_objects import GenericUUID


@pytest.mark.integration
def test_login_with_api_token(app, api_client):
    # arrange
    with app.transaction_context() as ctx:
        iam_service = ctx[IamService]
        iam_service.create_user(
            user_id=GenericUUID(int=1),
            email="admin@example.com",
            password="admin",
            access_token="token",
            is_superuser=True,
        )

    # act
    response = api_client.post(
        "/token", data={"username": "admin@example.com", "password": "admin"}
    )

    # assert
    assert response.status_code == 200
    assert response.json()["access_token"] == "token"


@pytest.mark.integration
def test_login_with_invalid_username_returns_400(app, api_client):
    # arrange
    with app.transaction_context() as ctx:
        iam_service = ctx[IamService]
        iam_service.create_user(
            user_id=GenericUUID(int=1),
            email="admin@example.com",
            password="admin",
            access_token="token",
            is_superuser=True,
        )

    # act
    response = api_client.post(
        "/token", data={"username": "john@example.com", "password": "password"}
    )

    # assert
    assert response.status_code == 400


@pytest.mark.integration
def test_login_with_invalid_password_returns_400(app, api_client):
    # arrange
    with app.transaction_context() as ctx:
        iam_service = ctx[IamService]
        iam_service.create_user(
            user_id=GenericUUID(int=1),
            email="admin@example.com",
            password="admin",
            access_token="token",
            is_superuser=True,
        )

    # act
    response = api_client.post(
        "/token",
        data={"username": "admin@example.com", "password": "incorrect_password"},
    )

    # assert
    assert response.status_code == 400
