from domain.value_objects import Currency

def test_currency_will_round_the_value():
    c = Currency(1.1234)
    assert c.amount == 1.12
