import logging
from os import getenv
from fastapi import FastAPI, Depends
from seedwork.infrastructure.request_context import request_context
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware


from seedwork.domain.value_objects import UUID
from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.infrastructure.logging import logger, LoggerFactory
from modules.catalog.domain.entities import Listing
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.command_handlers import create_listing_draft

from api.routers import catalog, users
from api.middleware import RequestContextPlugin
from config.api_config import ApiConfig
from config.container import Container


# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

# dependency injection container
container = Container()
container.config.from_pydantic(ApiConfig())

# API middleware
middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(RequestContextPlugin(container),),
    )
]

app = FastAPI(debug=container.config.DEBUG, middleware=middleware)

app.include_router(catalog.router)
app.include_router(users.router)
app.container = container


logger.info("using db engine %s" % str(container.engine()))


@app.get("/")
async def root():
    return {"info": "Online auctions API. See /docs for documentation"}


@app.get("/test")
async def test():
    import asyncio

    logger.debug("test1")
    await asyncio.sleep(3)
    logger.debug("test2")
    await asyncio.sleep(3)
    logger.debug("test3")
    await asyncio.sleep(3)
    logger.debug("test4")
    service = container.dummy_service()
    return {
        "service response": service.serve(),
        "correlation_id": request_context.correlation_id,
    }
