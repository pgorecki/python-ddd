import uuid


UUID = uuid.UUID
UUID.v4 = uuid.uuid4


class ValueObject:
    """
    Base class for value objects
    """


class Currency(int):
    pass
