import asyncio

from websocket import WebSocketBroadcaster


def test_broadcaster_sends_message_to_connected_clients():
    broadcaster = WebSocketBroadcaster()
    messages = []

    class DummySocket:
        async def send_text(self, message):
            messages.append(message)

    socket_a = DummySocket()
    socket_b = DummySocket()

    broadcaster.register(socket_a)
    broadcaster.register(socket_b)

    async def run_broadcast():
        await broadcaster.broadcast({"event": "confidence_update", "score": 0.9})

    asyncio.run(run_broadcast())

    assert len(messages) == 2
    assert 'confidence_update' in messages[0]
