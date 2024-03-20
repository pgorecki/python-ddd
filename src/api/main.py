import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.dependencies import oauth2_scheme  # noqa
from api.routers import bidding, catalog, diagnostics, iam
from config.api_config import ApiConfig
from config.container import create_application, ApplicationContainer
from seedwork.domain.exceptions import DomainException, EntityNotFoundException
from seedwork.infrastructure.database import Base
from seedwork.infrastructure.logging import LoggerFactory, logger

# configure logger prior to first usage
LoggerFactory.configure(logger_name="api")

# dependency injection container
config = ApiConfig()
container = ApplicationContainer(config=config)
db_engine = container.db_engine()
logger.info(f"using db engine {db_engine}, creating tables")
Base.metadata.create_all(db_engine)
logger.info("setup complete")

app = FastAPI(debug=config.DEBUG)

app.include_router(catalog.router)
app.include_router(bidding.router)
app.include_router(iam.router)
app.include_router(diagnostics.router)
app.container = container



try:
    import uuid

    from modules.iam.application.services import IamService

    with app.container.application().transaction_context() as ctx:
        iam_service = ctx[IamService]
        iam_service.create_user(
            user_id=uuid.UUID(int=1),
            email="user1@example.com",
            password="password",
            access_token="token",
        )
except ValueError as e:
    ...


@app.exception_handler(DomainException)
async def unicorn_exception_handler(request: Request, exc: DomainException):
    if container.config.DEBUG:
        raise exc

    return JSONResponse(
        status_code=500,
        content={"message": f"Oops! {exc} did something. There goes a rainbow..."},
    )


@app.exception_handler(EntityNotFoundException)
async def unicorn_exception_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Entity {exc.kwargs} not found in {exc.repository.__class__.__name__}"
        },
    )


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    finally:
        pass


@app.get("/")
async def root():
    return {"info": "Online auctions API. See /docs for documentation"}
