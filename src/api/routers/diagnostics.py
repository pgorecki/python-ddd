from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import (
    Application,
    User,
    get_authenticated_user,
    get_application,
)

from .iam import UserResponse

router = APIRouter()


@router.get("/debug", tags=["diagnostics"])
async def debug(
    app: Annotated[Application, Depends(get_application)],
    current_user: Annotated[User, Depends(get_authenticated_user)],
):
    return dict(
        app_id=id(app),
        name=app.name,
        version=app["app_version"],
        user=UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            access_token=current_user.access_token,
        ),
    )
