"""
Meeting Simulator

Publishes synthetic meeting events through the event bus.
Every event goes through confidence_handler → fusion_service → Postgres + WebSocket.
"""

import asyncio

from events.event_bus import event_bus
from events.event_handlers import confidence_handler, log_event
from events.event_types import EventType
from meeting_simulator.participant_generator import ParticipantGenerator
from meeting_simulator.event_generator import EventGenerator
from utils.logger import logger


# ── Subscribe confidence_handler to EVERY event type ─────────────────────────
_ALL_EVENTS = [
    EventType.PARTICIPANT_JOINED,
    EventType.PARTICIPANT_LEFT,
    EventType.DISPLAY_NAME_CHANGED,
    EventType.CAMERA_ON,
    EventType.CAMERA_OFF,
    EventType.CAMERA_NEVER_ON,
    EventType.MICROPHONE_ON,
    EventType.MICROPHONE_OFF,
    EventType.SCREEN_SHARE_STARTED,
    EventType.SCREEN_SHARE_STOPPED,
    EventType.SPEECH_STARTED,
    EventType.SPEECH_STOPPED,
    EventType.TRANSCRIPT_RECEIVED,
    EventType.NETWORK_LAG,
    EventType.SIMILAR_NAME_DETECTED,
    EventType.RECONNECTED,
]

for _evt in _ALL_EVENTS:
    event_bus.subscribe(_evt, log_event)
    event_bus.subscribe(_evt, confidence_handler)


async def run_simulation(meeting_id: int = 1):
    """
    Run the full meeting simulation asynchronously.
    Publishes events and awaits the fusion pipeline for each one.
    Returns a list of summary results for API reporting.
    """
    from services.fusion_service import fusion_service

    generator = ParticipantGenerator()
    participants = generator.generate()
    events = EventGenerator()
    summary = []

    def _record(label, evt, result, pid):
        if result:
            logger.info(f"[SIM] {label} -> confidence={result.confidence:.3f}")
            summary.append({
                "participant_id": pid,
                "event_type": getattr(evt, "type", str(label)),
                "confidence": round(result.confidence, 4),
                "reason": result.last_reason,
            })
        else:
            logger.info(f"[SIM] {label} -> no evidence matched")
            summary.append({
                "participant_id": pid,
                "event_type": getattr(evt, "type", str(label)),
                "confidence": None,
                "reason": "No evidence matched",
            })

    for participant in participants:
        logger.info(f"[SIM] Participant joining: {participant.participant_id}")

        # ── PARTICIPANT_JOINED ────────────────────────────────────────────────
        join_event = events.participant_join(meeting_id, participant)
        result = await fusion_service.process_event(join_event)
        _record("participant_join", join_event, result, participant.participant_id)

        if participant.participant_id == "candidate_001":

            # ── DISPLAY_NAME_CHANGED (device → real name) ─────────────────────
            changed_event = events.display_name_changed(
                meeting_id, participant,
                previous_display_name="MacBook Pro",
                new_display_name="John Doe",
            )
            result = await fusion_service.process_event(changed_event)
            _record("display_name_changed", changed_event, result, participant.participant_id)

            # ── CAMERA_ON ─────────────────────────────────────────────────────
            evt_on = events.camera_on(meeting_id, participant)
            result = await fusion_service.process_event(evt_on)
            _record("camera_on", evt_on, result, participant.participant_id)

            # ── CAMERA_OFF ────────────────────────────────────────────────────
            evt_off = events.camera_off(meeting_id, participant)
            result = await fusion_service.process_event(evt_off)
            _record("camera_off", evt_off, result, participant.participant_id)

            # ── CAMERA_ON (again) ─────────────────────────────────────────────
            evt_on2 = events.camera_on(meeting_id, participant)
            result = await fusion_service.process_event(evt_on2)
            _record("camera_on_2", evt_on2, result, participant.participant_id)

            # ── TRANSCRIPT_RECEIVED ───────────────────────────────────────────
            evt_trans1 = events.transcript_received(
                meeting_id, participant,
                transcript_text="Hello everyone, thank you for taking the time to interview me today.",
                speaker="candidate",
                confidence=0.98
            )
            result = await fusion_service.process_event(evt_trans1)
            _record("transcript_received", evt_trans1, result, participant.participant_id)

            evt_trans2 = events.transcript_received(
                meeting_id, participant,
                transcript_text="I have 5 years of experience building distributed backend architectures.",
                speaker="candidate",
                confidence=0.96
            )
            result = await fusion_service.process_event(evt_trans2)
            _record("transcript_received_2", evt_trans2, result, participant.participant_id)

        elif participant.participant_id == "interviewer_001":
            evt_trans_int = events.transcript_received(
                meeting_id, participant,
                transcript_text="Welcome! Let's get started with our system design architecture discussion.",
                speaker="interviewer",
                confidence=0.99
            )
            result = await fusion_service.process_event(evt_trans_int)
            _record("transcript_received", evt_trans_int, result, participant.participant_id)

    logger.info("[SIM] Simulation complete.")
    return summary


def _log_result(label, result):
    if result:
        logger.info(
            f"[SIM] {label} -> confidence={result.confidence:.3f}"
        )
    else:
        logger.info(f"[SIM] {label} -> no evidence matched")


def run():
    """Entry point for running the simulator standalone."""
    asyncio.run(run_simulation())


if __name__ == "__main__":
    run()