from application.services import IdentityHashingService


def test_hash():
    value = 'some_value'
    assert IdentityHashingService().hash(value=value) == value
