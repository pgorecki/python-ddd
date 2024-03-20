from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.dependencies import TransactionContext, get_transaction_context
from config.container import inject
from modules.iam.application.exceptions import InvalidCredentialsException
from modules.iam.application.services import IamService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


class UserResponse(BaseModel):
    id: str
    username: str
    access_token: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


# @router.get("/token", tags=["iam"])
# async def get_token(ctx: Annotated[TransactionContext, Depends(get_transaction_context_for_public_route)]):
#     return ctx.current_user.access_token


@router.post("/token", tags=["iam"])
@inject
async def login(
    ctx: Annotated[TransactionContext, Depends(get_transaction_context)],
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> LoginResponse:
    try:
        iam_service = ctx[IamService]
        user = iam_service.authenticate_with_name_and_password(
            form_data.username, form_data.password
        )
    except InvalidCredentialsException:
        # TODO: automatically map application exceptions to HTTP exceptions
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return LoginResponse(access_token=user.access_token, token_type="bearer")


@router.get("/users/me", tags=["iam"])
async def get_users_me(
    ctx: Annotated[TransactionContext, Depends(get_transaction_context)],
) -> UserResponse:
    user = ctx.current_user
    return UserResponse(
        id=str(user.id), username=user.username, access_token=user.access_token
    )
