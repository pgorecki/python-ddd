from fastapi import FastAPI, Depends
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware


from seedwork.domain.value_objects import UUID
from seedwork.infrastructure.repository import InMemoryRepository
from modules.catalog.domain.entities import Listing
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.command_handlers import create_listing_draft

from api.routers import catalog, users
from api.middleware import DependencyInjecionPlugin
from api.container import Container

from config.api_config import ApiConfig


# dependency injection container
container = Container()
container.config.from_pydantic(ApiConfig())

# API middleware
middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
            DependencyInjecionPlugin(container),
        ),
    )
]

app = FastAPI(debug=container.config.DEBUG, middleware=middleware)

app.include_router(catalog.router)
app.include_router(users.router)
app.container = container

logger = container.logger()
logger.info("using db engine %s" % str(container.engine()))


@app.get("/")
async def root():
    return {"info": "Online auctions API. See /docs for documentation"}


def request_container():
    container = context.get("container")
    with container.override():
        yield container


@app.get("/test")
async def test(container=Depends(request_container)):
    service = container.dummy_service()
    return {"service response": service.serve()}


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
