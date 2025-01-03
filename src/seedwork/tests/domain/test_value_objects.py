import pytest
from pydantic import BaseModel

from seedwork.domain.value_objects import GenericUUID, Money


class CustomPydanticModel(BaseModel):
    uuid: GenericUUID


@pytest.mark.unit
def test_money_equality():
    assert Money(10, "USD") == Money(10, "USD")


@pytest.mark.unit
def test_money_ordering():
    assert Money(10, "USD") < Money(100, "USD")
