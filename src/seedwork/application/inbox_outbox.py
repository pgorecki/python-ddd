import contextlib


class InMemoryInbox:
    def __init__(self):
        self.events = []

    def is_empty(self):
        return len(self.events) == 0

    @contextlib.contextmanager
    def get_next_event(self):
        yield self.events.pop(0)

    def enqueue(self, event):
        self.events.append(event)


class ProcessInboxUntilEmptyStrategy:
    def __init__(self, inbox: InMemoryInbox):
        self.inbox = inbox

    def should_process_next_event(self):
        return not self.inbox.is_empty()


class InMemoryOutbox:
    def __init__(self):
        self.events = []

    def save(self, event):
        self.events.append(event)
