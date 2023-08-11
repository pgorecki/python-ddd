from celery import Celery

from config.api_config import ApiConfig
from config.container import TopLevelContainer
from seedwork.application.inbox_outbox import (
    Inbox,
    Outbox,
    move_events_from_outbox_to_inbox,
)

c = Celery("hello", broker="amqp://guest@localhost//")

container = TopLevelContainer()
container.config.from_pydantic(ApiConfig())

app = container.application()


@c.task
def send_events_from_outbox_to_inbox():
    with app.transaction_context() as ctx:
        ctx.call(move_events_from_outbox_to_inbox)


@c.task
def process_incoming_events():
    def handle_incoming_events(ctx, inbox):
        while event := inbox.get_next_pending():
            try:
                ctx.handle_integration_event(event)
                inbox.mark_as_processed()
            except:
                inbox.mark_as_failed()

    with app.transaction_context() as ctx:
        ctx.call(handle_incoming_events)
