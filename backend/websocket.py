import json
from typing import List


class WebSocketBroadcaster:

    def __init__(self):
        self.clients: List[object] = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)

    async def broadcast(self, payload: dict):
        """Broadcast a raw payload dict to all connected clients."""
        message = json.dumps(payload, default=str)
        dead_clients = []
        for client in list(self.clients):
            try:
                await client.send_text(message)
            except Exception:
                dead_clients.append(client)
        for client in dead_clients:
            self.unregister(client)

    async def broadcast_confidence(
        self,
        participant_id: str,
        confidence: float,
        reason: str = None,
        evidence_type: str = None,
    ):
        """Convenience helper — broadcast a confidence update event."""
        await self.broadcast({
            "type": "confidence_updated",
            "participant_id": participant_id,
            "confidence": confidence,
            "reason": reason,
            "evidence_type": evidence_type,
        })

    async def broadcast_evidence(
        self,
        participant_id: str,
        evidence_type: str,
        confidence_delta: float,
        reason: str = None,
    ):
        """Convenience helper — broadcast a new evidence event."""
        await self.broadcast({
            "type": "evidence_collected",
            "participant_id": participant_id,
            "evidence_type": evidence_type,
            "confidence_delta": confidence_delta,
            "reason": reason,
        })

    async def broadcast_explanation(
        self,
        participant_id: str,
        explanation: str,
        evidence_type: str = None,
    ):
        """Convenience helper — broadcast an explanation update."""
        await self.broadcast({
            "type": "explanation_updated",
            "participant_id": participant_id,
            "explanation": explanation,
            "evidence_type": evidence_type,
        })
