from seedwork.domain.value_objects import Money
from modules.catalog.domain.rules import ListingAskPriceMustBeGreaterThanZero


def test_AuctionItemPriceMustBeGreaterThanZero_rule():
    rule = ListingAskPriceMustBeGreaterThanZero(ask_price=Money(1))
    assert not rule.is_broken()


def test_AuctionItemPriceMustBeGreaterThanZero_rule_is_broken():
    rule = ListingAskPriceMustBeGreaterThanZero(ask_price=Money(0))
    assert rule.is_broken()
