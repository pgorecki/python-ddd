from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from lato import Application, TransactionContext

from modules.iam.application.services import IamService
from modules.iam.domain.entities import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_application(request: Request) -> Application:
    return request.state.lato_application


async def get_transaction_context(
    app: Annotated[Application, Depends(get_application)],
) -> TransactionContext:
    """Creates a new transaction context for each request"""
    async with app.transaction_context() as ctx:
        yield ctx


async def get_authenticated_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    ctx: Annotated[TransactionContext, Depends(get_transaction_context)],
) -> User:
    current_user = ctx[IamService].find_user_by_access_token(access_token)
    return current_user
