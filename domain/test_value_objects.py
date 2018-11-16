from domain.value_objects import Currency

def test_currency_will_round_the_value():
    c = Currency(1.1234)
    assert c.amount == 1.12

def test_can_add_2_currencies():
    amount1 = Currency(10)
    amount2 = Currency(1)
    sum = amount1 + amount2
    assert sum.amount == 11

def test_can_subtact_2_currencies():
    amount1 = Currency(10)
    amount2 = Currency(1)
    diff = amount1 - amount2
    assert diff.amount == 9

def test_can_compare_currencies():
    assert Currency(1) == Currency(1)
    assert Currency(10) > Currency(1)
    assert Currency(1) < Currency(10)

def test_currenct_repr():
    assert str(Currency(1)) == '1.00'
