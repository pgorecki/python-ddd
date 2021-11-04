from fastapi import APIRouter, Depends
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.container import Container, inject
from modules.iam.module import IdentityAndAccessModule
from modules.iam.application.exceptions import (
    UserNotFoundException,
    UsernamePasswordMismatchException,
)
from modules.iam.domain.entities import User
from api.shared import dependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


def get_user_by_token(
    token,
    module: IdentityAndAccessModule = dependency(Container.iam_module),
) -> User:
    user = module.authentication_service.find_user_by_access_token(token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = get_user_by_token(token)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active():
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/token", tags=["iam"])
async def get_token(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.post("/token", tags=["iam"])
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    module: IdentityAndAccessModule = dependency(Container.iam_module),
):
    try:
        access_token = module.authentication_service.authenticate_with_password(
            form_data.username, form_data.password
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    except UsernamePasswordMismatchException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", tags=["iam"])
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
