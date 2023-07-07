from collections import OrderedDict


class OrderedSet(OrderedDict):
    def __init__(self, iterable=None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        self[item] = None

    def update(self, iterable):
        for item in iterable:
            self.add(item)
