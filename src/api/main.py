from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware
from sqlalchemy import create_engine

from seedwork.domain.value_objects import UUID
from seedwork.infrastructure.repository import InMemoryRepository
from modules.catalog.domain.entities import Listing
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.command_handlers import create_listing_draft

import api.config as config
from api.routers import catalog, users

# database engine
engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)


middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    )
]

app = FastAPI(debug=config.DEBUG, middleware=middleware)

app.include_router(catalog.router)
app.include_router(users.router)
app.engine = engine


@app.get("/")
async def root():
    return {"info": "Online auctions API. See /docs for documentation"}


@app.get("/test")
async def test():
    print((context.get("X-Request-ID")))
    return {"test": "test"}


# ####
# from fastapi import Depends


# def common_parameters(x: str, y: int):
#     print(args, kwargs)
#     return None


# def common_parameters2(z: int = 10):
#     print(args, kwargs)
#     return None


# def get_context():
#     context = object()
#     context.correlation_id = "1234"
#     return context


# @app.get("/dependency")
# async def root(
#     # foo=Depends(common_parameters),
#     # bar=Depends(common_parameters2),
#     context=Depends(get_context),
# ):
#     # print(request)
#     return {
#         "info": "Online auctions API. See /docs for documentation "
#         + context.correlation_id
#     }
