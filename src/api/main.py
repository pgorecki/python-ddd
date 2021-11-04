import time
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from seedwork.infrastructure.request_context import request_context
from seedwork.infrastructure.logging import logger, LoggerFactory

from api.routers import catalog, iam
from api.models import CurrentUser
from config.api_config import ApiConfig
from config.container import Container
import api.routers.catalog

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

# dependency injection container
container = Container()
container.config.from_pydantic(ApiConfig())
container.wire(modules=[api.routers.catalog, api.routers.iam])

app = FastAPI(debug=container.config.DEBUG)
app.include_router(catalog.router)
app.include_router(iam.router)
app.container = container


logger.info("using db engine %s" % str(container.engine()))


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    start_time = time.time()
    request_context.begin_request(current_user=CurrentUser.fake_user())
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    finally:
        request_context.end_request()


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
