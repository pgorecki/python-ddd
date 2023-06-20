from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_transaction_context
from seedwork.application import TransactionContext

from .iam import UserResponse

router = APIRouter()


@router.get("/debug", tags=["diagnostics"])
async def debug(ctx: Annotated[TransactionContext, Depends(get_transaction_context)]):
    return dict(
        app_id=id(ctx.app),
        user=UserResponse(
            id=str(ctx.current_user.id), username=ctx.current_user.username
        ),
        name=ctx.app.name,
        version=ctx.app.version,
    )
