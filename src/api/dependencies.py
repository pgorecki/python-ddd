from fastapi import Header, HTTPException
from pydantic import BaseModel
from seedwork.domain.value_objects import UUID

from dataclasses import dataclass


class CurrentUser(BaseModel):
    id: UUID
    username = "fake_current_user"
    email = "fake@email.com"
    is_admin = True


class Logger:
    ...


@dataclass
class RequestContext:
    current_user: CurrentUser
    logger: Logger


def request_context():
    return RequestContext(
        current_user=CurrentUser(id=UUID("{12345678-1234-5678-1234-567812345678}")),
        logger=Logger(),
    )
