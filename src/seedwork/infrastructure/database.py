import json
import logging
import uuid

from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import force_auto_coercion

logger = logging.getLogger(__name__)


force_auto_coercion()
Base = declarative_base()


def _default(val):
    if isinstance(val, uuid.UUID):
        return str(val)
    raise TypeError()


def dumps(d):
    return json.dumps(d, default=_default)
