from collections import defaultdict

from events.event import Event


class EventBus:

    def __init__(self):

        self.subscribers = defaultdict(list)

    def subscribe(
        self,
        event_type,
        callback
    ):

        self.subscribers[event_type].append(callback)

    def publish(
        self,
        event: Event
    ):

        callbacks = self.subscribers.get(
            event.type,
            []
        )

        for callback in callbacks:

            callback(event)


event_bus = EventBus()