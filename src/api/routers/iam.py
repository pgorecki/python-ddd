from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.dependencies import (
    Application,
    TransactionContext,
    get_application,
    get_transaction_context,
)
from config.container import inject
from modules.iam.application.exceptions import InvalidCredentialsException
from modules.iam.application.services import IamService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


class UserResponse(BaseModel):
    id: str
    username: str


@router.get("/token", tags=["iam"])
async def get_token(app: Annotated[Application, Depends(get_application)]):
    return app.current_user.access_token


@router.post("/token", tags=["iam"])
@inject
async def login(
    ctx: Annotated[TransactionContext, Depends(get_transaction_context)],
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    try:
        iam_service = ctx.get_service(IamService)
        user = iam_service.authenticate_with_name_and_password(
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
async def get_users_me(
    app: Annotated[Application, Depends(get_application)],
):
    return app.current_user
