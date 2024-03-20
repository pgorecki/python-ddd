import pytest

from modules.iam.application.services import IamService
from seedwork.domain.value_objects import GenericUUID


@pytest.mark.integration
def test_create_user_with_duplicated_email_raises_exception(app):
    # arrange
    with app.transaction_context() as ctx:
        iam_service = ctx[IamService]
        iam_service.create_user(
            user_id=GenericUUID(int=1),
            email="user1@example.com",
            password="password",
            access_token="token",
        )

    # assert
    with pytest.raises(ValueError):
        # act
        with app.transaction_context() as ctx:
            iam_service = ctx[IamService]
            iam_service.create_user(
                user_id=GenericUUID(int=2),
                email="user2@example.com",
                password="password",
                access_token="token",
            )


@pytest.mark.integration
def test_create_user_with_duplicated_access_token_raises_exception(app):
    # arrange
    with app.transaction_context() as ctx:
        ctx[IamService].create_user(
            user_id=GenericUUID(int=1),
            email="user1@example.com",
            password="password",
            access_token="token",
        )

    # assert
    with pytest.raises(ValueError):
        # act
        with app.transaction_context() as ctx:
            ctx[IamService].create_user(
                user_id=GenericUUID(int=2),
                email="user2@example.com",
                password="password",
                access_token="token",
            )
