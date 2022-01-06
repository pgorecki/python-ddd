from seedwork.domain.value_objects import Money
from modules.catalog.domain.rules import ListingPriceMustBeGreaterThanZero


def test_AuctionItemPriceMustBeGreaterThanZero_rule():
    rule = ListingPriceMustBeGreaterThanZero(price=Money(1))
    assert not rule.is_broken()


def test_AuctionItemPriceMustBeGreaterThanZero_rule_is_broken():
    rule = ListingPriceMustBeGreaterThanZero(price=Money(0))
    assert rule.is_broken()
