from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import (
    TransactionContext,
    User,
    get_authenticated_user,
    get_transaction_context,
)

from .iam import UserResponse

router = APIRouter()


@router.get("/debug", tags=["diagnostics"])
async def debug(
    ctx: Annotated[TransactionContext, Depends(get_transaction_context)],
    current_user: Annotated[User, Depends(get_authenticated_user)],
):
    return dict(
        app_id=id(ctx.app),
        name=ctx.app.name,
        version=ctx.app.version,
        user=UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            access_token=current_user.access_token,
        ),
    )
