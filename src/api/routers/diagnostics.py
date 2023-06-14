from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import allow_anonymous, create_app
from seedwork.application import Application

router = APIRouter()


from .iam import UserResponse

app_for_anonymous = create_app(allow_anonymous())


@router.get("/debug", tags=["diagnostics"])
async def debug(app: Annotated[Application, Depends(app_for_anonymous)]):
    return dict(
        app_id=id(app),
        user=UserResponse(
            id=str(app.current_user.id), username=app.current_user.username
        ),
        name=app.name,
        version=app.version,
    )
