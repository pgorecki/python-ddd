import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from sqlalchemy.orm import Session

from modules.catalog.application.command import (
    CreateListingDraftCommand,
    PublishListingCommand,
    UpdateListingDraftCommand,
)
from modules.catalog.application.command.create_listing_draft import (
    create_listing_draft,
)
from modules.catalog.application.query import GetAllListings
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from seedwork.application.decorators import registry
from seedwork.infrastructure.request_context import request_context


def handles_command(command_class):
    ...


def handles_query(query_class):
    ...


class implemented_as:
    def __init__(self, repo_class):
        self.repo_class = repo_class

    def __get__(self, obj, obj_type=None):
        raise NotImplementedError()


def get_arg(name, kwargs1, kwargs2):
    return kwargs1.get(name, None) or kwargs2.get(name)


@dataclass
class UnitOfWork:
    db_session: Session
    correlation_id: uuid.UUID
    listing_repository: ListingRepository


class CatalogModule:
    handles_command(CreateListingDraftCommand)
    handles_query(GetAllListings)

    def __init__(self, **kwargs):
        self._uow: ContextVar[UnitOfWork] = ContextVar("_uow", default=None)
        self.extra_kwargs = kwargs

    @contextmanager
    def unit_of_work(self, **kwargs):
        engine = get_arg("engine", kwargs, self.extra_kwargs)
        correlation_id = uuid.uuid4()
        db_session = None
        with Session(engine) as db_session:
            uow = UnitOfWork(
                correlation_id=correlation_id,
                db_session=db_session,
                listing_repository=PostgresJsonListingRepository(db_session=db_session),
            )
            # begin unit of work
            self._uow.set(uow)
            self.begin_unit_of_work(uow)
            yield uow
            self.end_unit_of_work(uow)
            # end unit of work
            self._uow.set(None)

    def begin_unit_of_work(self, uow: UnitOfWork):
        request_context.correlation_id.set(uow.correlation_id)

    def end_unit_of_work(self, uow):
        uow.listing_repository.persist_all()
        uow.db_session.commit()

    def configure(self, **kwargs):
        self.extra_kwargs = kwargs

    def execute_command(self, command):
        command_class = type(command)
        handler = registry.get_command_handler_for(command_class)
        kwargs = registry.get_command_handler_parameters_for(command_class)

        for param_name, param_type in kwargs.items():
            for attr in self.uow.__dict__.values():
                if isinstance(attr, param_type):
                    kwargs[param_name] = attr

        return handler(command=command, **kwargs)

    @property
    def uow(self) -> UnitOfWork:
        uow = self._uow.get()
        print(self._uow, self._uow.get())
        assert uow, "Unit of work not set, use context manager"
        return uow
