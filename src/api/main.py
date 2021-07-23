from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import ContextMiddleware

from seedwork.domain.value_objects import UUID
from seedwork.infrastructure.repository import InMemoryRepository
from modules.catalog.domain.entities import Listing
from modules.catalog.application.commands import CreateListingDraftCommand
from modules.catalog.application.command_handlers import create_listing_draft

import api.config as config
from api.routers import catalog, users

middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    )
]

app = FastAPI(debug=config.DEBUG)

app.include_router(catalog.router)
app.include_router(users.router)


@app.get("/")
async def root():
    # print(request)
    return {"info": "Online auctions API. See /docs for documentation"}
