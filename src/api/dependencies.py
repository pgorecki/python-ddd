from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from config.container import Container, inject
from modules.iam.domain.entities import User
from seedwork.application import Application

from .shared import dependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def allow_role(role: str):
    def check(user: User):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True

    return check


def allow_authenticated():
    def check(user: User):
        if not user.is_authenticated():
            raise HTTPException(status_code=403, detail="Forbidden")
        return True

    return check


def allow_anonymous():
    return lambda user: True


def create_app(check: callable) -> Callable[..., Application]:
    @inject
    async def create(
        request: Request, app: Application = dependency(Container.application)
    ):
        try:
            access_token = await oauth2_scheme(request=request)
            current_user = app.iam_service.find_user_by_access_token(access_token)
        except HTTPException as e:
            current_user = User.Anonymous()

        print("current user", current_user)
        check(current_user)
        app.current_user = current_user
        return app

    return create


def get_current_active_user(
    app: Application = Depends(create_app(allow_authenticated())),
):
    return app.current_user
