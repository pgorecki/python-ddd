from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.dependencies import get_current_active_user
from api.shared import dependency
from config.container import Container, inject
from modules.iam.application.exceptions import InvalidCredentialsException
from modules.iam.domain.entities import User
from seedwork.application import Application

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


class UserResponse(BaseModel):
    id: str
    username: str


@router.get("/token", tags=["iam"])
async def get_token(token: str = Depends(oauth2_scheme)):
    return "sample_token"


@router.post("/token", tags=["iam"])
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    app: Application = dependency(Container.application),
):
    try:
        user = app.iam_service.authenticate_with_password(
            form_data.username, form_data.password
        )
    except InvalidCredentialsException:
        # TODO: automatically map application exceptions to HTTP exceptions
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return {"access_token": user.access_token, "token_type": "bearer"}


@router.get("/users/me", tags=["iam"])
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
