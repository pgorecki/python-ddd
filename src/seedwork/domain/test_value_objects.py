from seedwork.domain.value_objects import Money


def test_money_equality():
    assert Money(10, "USD") == Money(10, "USD")


def test_money_ordering():
    assert Money(10, "USD") < Money(100, "USD")
