import uuid


UUID = uuid.UUID
UUID.v4 = uuid.uuid4


class Currency(int):
    pass
