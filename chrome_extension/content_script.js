/**
 * Sherlock AI Google Meet Bridge — Content Script
 * Runs inside https://meet.google.com/*
 * 1. Monitors participant display names in real time.
 * 2. Captures audio segments and POSTs them to local Sherlock backend for live evaluation.
 */

let isCapturing = false;
let mediaRecorder = null;
let captureInterval = null;
let apiUrl = "http://127.0.0.1:8000/api/v1";
let candidateName = "Candidate";

function extractMeetParticipants() {
  const names = new Set();
  // Standard Google Meet participant name elements
  document.querySelectorAll('[data-self-name], [data-participant-id], .zWGUib, .ZjFb7c').forEach(el => {
    const text = el.textContent?.trim();
    if (text && text.length > 1 && text.length < 50) {
      names.add(text);
    }
  });
  return Array.from(names);
}

async function startLiveAudioStream() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      if (!isCapturing || chunks.length === 0) return;
      const blob = new Blob(chunks, { type: "audio/webm" });
      chunks.length = 0; // reset

      // Upload audio chunk to local Sherlock API
      const formData = new FormData();
      formData.append("participant_id", "candidate_001");
      formData.append("meeting_id", "google_meet_live");
      formData.append("audio_file", blob, "live_meet_chunk.webm");

      try {
        await fetch(`${apiUrl}/audio/upload`, {
          method: "POST",
          body: formData,
        });
        console.log("[Sherlock Bridge] Uploaded 5s audio chunk for analysis.");
      } catch (err) {
        console.warn("[Sherlock Bridge] Could not connect to local Sherlock backend:", err);
      }

      if (isCapturing) {
        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), 5000);
      }
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 5000);
  } catch (err) {
    console.warn("[Sherlock Bridge] Microphone access not granted for live audio capture:", err);
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "START_CAPTURE") {
    apiUrl = request.apiUrl || apiUrl;
    candidateName = request.candidateName || candidateName;
    isCapturing = true;

    console.log("[Sherlock Bridge] Started live Google Meet capture pointing to:", apiUrl);
    startLiveAudioStream();

    // Roster monitoring loop
    captureInterval = setInterval(() => {
      const roster = extractMeetParticipants();
      console.log("[Sherlock Bridge] Active Meet Roster:", roster);
    }, 4000);
  } else if (request.action === "STOP_CAPTURE") {
    isCapturing = false;
    if (captureInterval) clearInterval(captureInterval);
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
    console.log("[Sherlock Bridge] Stopped live capture.");
  }
});
