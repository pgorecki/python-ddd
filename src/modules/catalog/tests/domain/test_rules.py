import pytest

from modules.catalog.domain.rules import ListingAskPriceMustBeGreaterThanZero
from seedwork.domain.value_objects import Money


@pytest.mark.unit
def test_AuctionItemPriceMustBeGreaterThanZero_rule():
    rule = ListingAskPriceMustBeGreaterThanZero(ask_price=Money(1))
    assert not rule.is_broken()


@pytest.mark.unit
def test_AuctionItemPriceMustBeGreaterThanZero_rule_is_broken():
    rule = ListingAskPriceMustBeGreaterThanZero(ask_price=Money(0))
    assert rule.is_broken()
