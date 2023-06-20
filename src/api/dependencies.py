from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from modules.iam.application.services import IamService
from modules.iam.domain.entities import AnonymousUser
from seedwork.application import Application, TransactionContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_application(request: Request) -> Application:
    application = request.app.container.application()
    return application


async def get_transaction_context(
    request: Request, app: Annotated[Application, Depends(get_application)]
) -> TransactionContext:
    """Creates a new transaction context for each request"""

    with app.transaction_context() as ctx:
        try:
            access_token = await oauth2_scheme(request=request)
            current_user = ctx.get_service(IamService).find_user_by_access_token(
                access_token
            )
        except HTTPException as e:
            current_user = AnonymousUser()

        ctx.dependency_provider["current_user"] = current_user

        yield ctx
