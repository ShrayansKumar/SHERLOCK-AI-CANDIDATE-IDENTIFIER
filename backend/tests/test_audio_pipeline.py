import io
import os
import wave
import struct
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def _create_dummy_wav_bytes() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        for _ in range(16000):
            wf.writeframes(struct.pack("<h", 0))
    buf.seek(0)
    return buf.read()


def test_audio_upload_unsupported_format():
    response = client.post(
        "/api/v1/audio/upload",
        data={"participant_id": "test_candidate", "meeting_id": "test_meet"},
        files={"audio_file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_audio_upload_success():
    wav_bytes = _create_dummy_wav_bytes()
    response = client.post(
        "/api/v1/audio/upload",
        data={"participant_id": "candidate_audio_test", "meeting_id": "meet_audio_test"},
        files={"audio_file": ("test.wav", io.BytesIO(wav_bytes), "audio/wav")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "upload_id" in data
    assert data["participant_id"] == "candidate_audio_test"
    assert data["meeting_id"] == "meet_audio_test"
    assert data["file_format"] == "wav"
    assert "evidence_generated" in data
    assert "confidence" in data


def test_get_audio_by_participant():
    response = client.get("/api/v1/audio/candidate_audio_test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["participant_id"] == "candidate_audio_test" for item in data)


def test_get_audio_by_meeting():
    response = client.get("/api/v1/audio/meeting/meet_audio_test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["meeting_id"] == "meet_audio_test" for item in data)
