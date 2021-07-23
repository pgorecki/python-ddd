from fastapi import APIRouter, Depends
from api.dependencies import request_context, RequestContext

router = APIRouter()


@router.get("/users", tags=["users"])
async def user_list():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def current_user_details(context: RequestContext = Depends(request_context)):
    return context.current_user


@router.get("/users/{username}", tags=["users"])
async def user_details(username: str):
    return {"username": username}
