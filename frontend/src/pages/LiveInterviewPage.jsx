import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import useWebSocket from "../hooks/useWebSocket";
import { endInterview, getMeetings } from "../services/meetingService";
import { getParticipantConfidence, getConfidenceTimeline } from "../services/confidenceService";
import { getParticipantExplanations } from "../services/explanationService";
import { getParticipantTranscripts } from "../services/transcriptService";
import api from "../services/api";
import {
  Mic, MicOff, Video, VideoOff, Square, Wifi, WifiOff,
  Clock, ShieldCheck, Activity, TrendingUp, FileText,
  CheckCircle2, AlertTriangle, Radio, UploadCloud,
  Headphones, Sliders, HelpCircle, RotateCcw,
} from "lucide-react";

/* ─── constants ──────────────────────────────────────────────────────────── */
const CANDIDATE_ID   = "candidate_001";
const AUDIO_INTERVAL = 10000; // send audio every 10 s
const VIDEO_INTERVAL = 8000;  // send video frame every 8 s

/* ─── Session Timer ─────────────────────────────────────────────────────── */
function SessionTimer({ startedAt }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    return () => clearInterval(id);
  }, [startedAt]);
  const pad = (n) => String(n).padStart(2, "0");
  const h = Math.floor(elapsed / 3600), m = Math.floor((elapsed % 3600) / 60), s = elapsed % 60;
  return <span className="font-mono text-xl font-bold text-slate-800">{pad(h)}:{pad(m)}:{pad(s)}</span>;
}

/* ─── Circular Gauge ────────────────────────────────────────────────────── */
function Gauge({ pct }) {
  const r = 54, circ = 2 * Math.PI * r;
  const color = pct >= 75 ? "#10b981" : pct >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div className="relative inline-flex items-center justify-center w-36 h-36">
      <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} stroke="#e2e8f0" strokeWidth="10" fill="transparent" />
        <circle cx="60" cy="60" r={r} stroke={color} strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={circ - (pct / 100) * circ}
          strokeLinecap="round" fill="transparent"
          style={{ transition: "stroke-dashoffset 1s ease-out, stroke 0.5s" }} />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-extrabold text-slate-800 leading-none">{pct}%</span>
        <span className="text-[10px] text-slate-400 font-semibold uppercase mt-0.5">confidence</span>
      </div>
    </div>
  );
}

/* ─── Status pill ───────────────────────────────────────────────────────── */
function Pill({ on, onLabel, offLabel, icon: On, offIcon: Off }) {
  const Icon = on ? On : Off;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border transition ${
      on ? "bg-emerald-50 border-emerald-200 text-emerald-700"
         : "bg-slate-100 border-slate-200 text-slate-500"
    }`}>
      <Icon size={12} />{on ? onLabel : offLabel}
    </span>
  );
}

/* ─── Stat Card ──────────────────────────────────────────────────────────── */
function StatCard({ label, value, sub, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
      <div className="flex items-center justify-between mb-1">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</p>
        <Icon size={15} className={color} />
      </div>
      <p className="text-2xl font-extrabold text-slate-800">{value}</p>
      <p className="text-xs text-slate-400 mt-0.5">{sub}</p>
    </div>
  );
}

/* ─── Upload log entry ───────────────────────────────────────────────────── */
function LogEntry({ entry }) {
  const colors = { ok: "text-emerald-600", err: "text-red-500", sending: "text-blue-500" };
  const icons = { ok: CheckCircle2, err: AlertTriangle, sending: UploadCloud };
  const Icon = icons[entry.status] || UploadCloud;
  return (
    <div className="flex items-start gap-2 text-xs py-1 border-b border-slate-50 last:border-0">
      <Icon size={12} className={`${colors[entry.status]} flex-shrink-0 mt-0.5`} />
      <span className="text-slate-500 flex-shrink-0">{entry.time}</span>
      <span className="text-slate-700">{entry.msg}</span>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════
   MAIN PAGE
══════════════════════════════════════════════════════════════════════════ */
export default function LiveInterviewPage() {
  const { meetingDbId } = useParams();
  const navigate = useNavigate();

  /* meeting info */
  const [meeting, setMeeting] = useState(null);
  const [sessionStart] = useState(Date.now());

  /* capture state */
  const [capturing, setCapturing] = useState(false);
  const [micOn, setMicOn]         = useState(false);
  const [camOn, setCamOn]         = useState(false);
  const [ending, setEnding]       = useState(false);
  const [permError, setPermError] = useState(null);

  /* audio source & VB-Cable setup */
  const [audioSource, setAudioSource] = useState("vb_cable"); // "vb_cable" | "tab_audio" | "browser_mic"
  const [vbDeviceInfo, setVbDeviceInfo] = useState(null);
  const [vbCaptureStatus, setVbCaptureStatus] = useState(null);
  const [showVbGuide, setShowVbGuide] = useState(false);

  /* live data */
  const [confidence, setConfidence] = useState(0);        // 0-100
  const [evidenceCount, setEvidenceCount] = useState(0);
  const [transcriptCount, setTranscriptCount] = useState(0);
  const [timelineCount, setTimelineCount] = useState(0);
  const [timeline, setTimeline] = useState([]);
  const [explanations, setExplanations] = useState([]);
  const [transcripts, setTranscripts] = useState([]);
  const [uploadLog, setUploadLog] = useState([]);

  /* refs for media */
  const audioStreamRef   = useRef(null);
  const videoStreamRef   = useRef(null);
  const audioRecorderRef = useRef(null);
  const audioChunksRef   = useRef([]);
  const videoRef         = useRef(null);       // <video> element for webcam preview
  const canvasRef        = useRef(null);       // offscreen canvas for frame grabs
  const audioTimerRef    = useRef(null);
  const videoTimerRef    = useRef(null);
  const meetingStrIdRef  = useRef(`session_${meetingDbId}`);

  /* ── load meeting ─────────────────────────────────────────────────────── */
  useEffect(() => {
    getMeetings().then((list) => {
      const found = list.find((m) => String(m.id) === String(meetingDbId));
      if (found) {
        meetingStrIdRef.current = found.meeting_id;
        setMeeting(found);
      }
    }).catch(() => {});
  }, [meetingDbId]);

  /* ── fetch backend data ───────────────────────────────────────────────── */
  const log = useCallback((msg, status = "ok") => {
    const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    setUploadLog((prev) => [{ msg, status, time }, ...prev].slice(0, 30));
  }, []);

  const refreshAll = useCallback(async () => {
    try {
      const [conf, tl, exp, tx] = await Promise.allSettled([
        getParticipantConfidence(CANDIDATE_ID),
        getConfidenceTimeline(CANDIDATE_ID),
        getParticipantExplanations(CANDIDATE_ID),
        getParticipantTranscripts(CANDIDATE_ID),
      ]);

      if (conf.status === "fulfilled") {
        const pct = Math.round((conf.value?.confidence ?? 0) * 100);
        setConfidence(pct);
      }
      if (tl.status === "fulfilled") {
        setTimeline(tl.value || []);
        setTimelineCount((tl.value || []).length);
      }
      if (exp.status === "fulfilled") {
        setExplanations(exp.value || []);
        setEvidenceCount((exp.value || []).length);
      }
      if (tx.status === "fulfilled") {
        setTranscripts(tx.value || []);
        setTranscriptCount((tx.value || []).length);
      }
    } catch { /* silent */ }
  }, []);

  /* initial load */
  useEffect(() => {
    refreshAll();
    api.get("/audio/devices").then((res) => {
      setVbDeviceInfo(res.data);
      if (res.data?.vb_cable_index !== null && res.data?.vb_cable_index !== undefined) {
        log(`VB-Cable detected: ${res.data.vb_cable_name} (index ${res.data.vb_cable_index})`, "ok");
      }
    }).catch(() => {});
  }, [refreshAll, log]);

  /* poll backend VB-Cable status while capturing */
  useEffect(() => {
    if (!capturing || audioSource !== "vb_cable") return;
    const interval = setInterval(() => {
      api.get("/audio/live-capture/status").then((res) => {
        setVbCaptureStatus(res.data);
        if (res.data?.chunks_processed > 0) {
          refreshAll();
        }
      }).catch(() => {});
    }, 4000);
    return () => clearInterval(interval);
  }, [capturing, audioSource, refreshAll]);

  /* ── WebSocket live updates ───────────────────────────────────────────── */
  const onWsEvent = useCallback((data) => {
    if (data.confidence !== undefined && data.participant_id === CANDIDATE_ID) {
      setConfidence(Math.round(data.confidence * 100));
    }
    if (data.type === "new_transcript" && data.text) {
      setTranscripts((prev) => [
        ...prev,
        {
          id: Date.now(),
          participant_id: data.participant_id ?? CANDIDATE_ID,
          speaker: data.speaker ?? "candidate",
          text: data.text,
          confidence: data.confidence ?? 0.95,
          created_at: new Date().toISOString(),
        },
      ]);
      setTranscriptCount((prev) => prev + 1);
    }
    refreshAll();
  }, [refreshAll]);

  const { connected } = useWebSocket({
    onConfidence: onWsEvent,
    onEvidence: onWsEvent,
    onTranscript: onWsEvent,
    onRaw: onWsEvent,
  });

  /* ── audio capture loop ───────────────────────────────────────────────── */
  const sendAudioChunk = useCallback(async (blob) => {
    if (blob.size < 1000) return; // skip silence chunks
    log(`Sending ${Math.round(blob.size / 1024)} KB audio chunk…`, "sending");
    const fd = new FormData();
    fd.append("participant_id", CANDIDATE_ID);
    fd.append("meeting_id", meetingStrIdRef.current);
    fd.append("audio_file", blob, "live_chunk.webm");
    try {
      await api.post("/audio/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      log("Audio chunk analysed ✓", "ok");
    } catch (err) {
      log(`Audio upload failed: ${err?.response?.data?.detail ?? err.message}`, "err");
    }
  }, [log]);

  const startAudioCapture = useCallback(async () => {
    try {
      let stream;
      if (audioSource === "tab_audio") {
        stream = await navigator.mediaDevices.getDisplayMedia({ audio: true, video: true });
      } else {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      audioStreamRef.current = stream;
      setMicOn(true);
      setPermError(null);

      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      audioRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        audioChunksRef.current = [];
        sendAudioChunk(blob);
      };

      const tick = () => {
        if (recorder.state === "recording") recorder.stop();
        recorder.start();
        audioTimerRef.current = setTimeout(tick, AUDIO_INTERVAL);
      };
      recorder.start();
      audioTimerRef.current = setTimeout(tick, AUDIO_INTERVAL);

      log("Browser audio capture started ✓", "ok");
    } catch (err) {
      setPermError("Audio capture permission denied or cancelled.");
      log("Audio access denied/cancelled", "err");
    }
  }, [audioSource, sendAudioChunk, log]);

  /* ── video / webcam capture loop ─────────────────────────────────────── */
  const sendVideoFrame = useCallback(async () => {
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;

    canvas.width  = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, 640, 480);

    canvas.toBlob(async (blob) => {
      if (!blob || blob.size < 500) return;
      log(`Sending webcam frame (${Math.round(blob.size / 1024)} KB)…`, "sending");

      const fd = new FormData();
      fd.append("participant_id", CANDIDATE_ID);
      fd.append("meeting_id", meetingStrIdRef.current);
      fd.append("video_file", blob, "frame.jpg");

      try {
        await api.post("/video/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
        log("Video frame analysed ✓", "ok");
      } catch (err) {
        log(`Video frame failed: ${err?.response?.data?.detail ?? err.message}`, "err");
      }
    }, "image/jpeg", 0.85);
  }, [log]);

  const startVideoCapture = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      videoStreamRef.current = stream;
      setCamOn(true);

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }

      const tick = () => {
        sendVideoFrame();
        videoTimerRef.current = setTimeout(tick, VIDEO_INTERVAL);
      };
      videoTimerRef.current = setTimeout(tick, 2000);

      log("Webcam capture started ✓", "ok");
    } catch (err) {
      log("Camera access denied (continuing audio-only)", "err");
    }
  }, [sendVideoFrame, log]);

  const handleResetSession = useCallback(async () => {
    try {
      await api.delete(`/transcripts/clear/${CANDIDATE_ID}`);
      setTranscripts([]);
      setTranscriptCount(0);
      log("Session transcripts cleared. Clean state ready!", "ok");
    } catch (err) {
      log("Failed to clear historical transcripts", "err");
    }
  }, [log]);

  /* ── start / stop capture ─────────────────────────────────────────────── */
  const startCapture = useCallback(async () => {
    setCapturing(true);
    if (audioSource === "vb_cable") {
      log("Starting VB-Audio Cable live listener on backend…", "sending");
      try {
        const res = await api.post("/audio/live-capture/start", {
          meeting_id: meetingStrIdRef.current,
          participant_id: CANDIDATE_ID,
          device_index: vbDeviceInfo?.vb_cable_index,
          chunk_seconds: 10,
        });
        setMicOn(true);
        setPermError(null);
        log(`VB-Cable active: ${res.data.device_name}`, "ok");
      } catch (e) {
        log("VB-Cable backend start failed. Check backend server.", "err");
        setPermError("Could not connect to VB-Cable backend listener. Please restart backend server.");
      }
    } else {
      await startAudioCapture();
    }
    try {
      await startVideoCapture();
    } catch (e) {
      log("Video capture continue audio-only", "err");
    }
  }, [audioSource, vbDeviceInfo, startAudioCapture, startVideoCapture, log]);

  const stopCapture = useCallback(() => {
    clearTimeout(audioTimerRef.current);
    clearTimeout(videoTimerRef.current);

    if (audioRecorderRef.current?.state === "recording") audioRecorderRef.current.stop();
    audioStreamRef.current?.getTracks().forEach((t) => t.stop());
    videoStreamRef.current?.getTracks().forEach((t) => t.stop());

    if (videoRef.current) videoRef.current.srcObject = null;

    if (audioSource === "vb_cable") {
      api.post("/audio/live-capture/stop").catch(() => {});
    }

    setMicOn(false);
    setCamOn(false);
    setCapturing(false);
    log("Capture stopped", "ok");
  }, [audioSource, log]);

  /* cleanup on unmount */
  useEffect(() => () => stopCapture(), [stopCapture]);

  /* ── end interview ───────────────────────────────────────────────────── */
  const handleEnd = async () => {
    if (!window.confirm("End this interview session and go to the final report?")) return;
    stopCapture();
    setEnding(true);
    try {
      await endInterview(meetingDbId);
      navigate("/report");
    } catch {
      setEnding(false);
    }
  };

  /* ─────────────────────────────────────────────────────────────────────── */
  const riskLabel = confidence >= 80 ? "Low Risk" : confidence >= 60 ? "Medium Risk" : confidence >= 40 ? "High Risk" : "Critical";
  const riskCls   = confidence >= 80 ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : confidence >= 60 ? "bg-amber-50 text-amber-700 border-amber-200"
                  : "bg-red-50 text-red-700 border-red-200";

  /* ──────────────────────────────────────────────────────────────────────── */
  return (
    <MainLayout>
      {/* Hidden canvas for frame grabs */}
      <canvas ref={canvasRef} className="hidden" />

      <div className="space-y-4">

        {/* ── Header bar ─────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <Activity className="text-blue-600" size={24} />
                Live Interview
              </h1>
              {capturing && (
                <span className="px-2.5 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-bold animate-pulse flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" /> REC
                </span>
              )}
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${connected ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-slate-100 text-slate-500 border-slate-200"}`}>
                {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
                {connected ? "WS Live" : "WS Off"}
              </span>
            </div>
            {meeting && (
              <p className="text-slate-500 text-sm mt-0.5">
                {meeting.platform} · <span className="font-mono">{meeting.meeting_id}</span>
                {meeting.candidate_name && ` · ${meeting.candidate_name}`}
                {meeting.job_role && ` · ${meeting.job_role}`}
              </p>
            )}
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2 text-slate-500">
              <Clock size={16} className="text-slate-400" />
              <SessionTimer startedAt={sessionStart} />
            </div>
            <button onClick={handleResetSession}
              title="Clear previous test transcript data"
              className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition border border-slate-200">
              <RotateCcw size={14} /> Clear Transcript
            </button>
            {!capturing ? (
              <button onClick={startCapture}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition shadow-sm">
                <Radio size={15} /> Start Capture
              </button>
            ) : (
              <button onClick={stopCapture}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-800 text-white font-semibold text-sm transition">
                <MicOff size={15} /> Pause Capture
              </button>
            )}
            <button onClick={handleEnd} disabled={ending}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-sm transition shadow-sm disabled:opacity-60">
              <Square size={14} />
              {ending ? "Ending…" : "End Interview"}
            </button>
          </div>
        </div>

        {/* ── Audio Capture Source Selector & VB-Cable Panel ────────────── */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Headphones className="text-blue-600" size={18} />
              <span className="text-sm font-bold text-slate-700">Meeting Audio Capture Source:</span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                disabled={capturing}
                onClick={() => setAudioSource("vb_cable")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center gap-1.5 ${
                  audioSource === "vb_cable"
                    ? "bg-blue-50 border-blue-300 text-blue-700 font-bold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                🎧 VB-Audio Cable (Backend Python)
              </button>
              <button
                type="button"
                disabled={capturing}
                onClick={() => setAudioSource("tab_audio")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center gap-1.5 ${
                  audioSource === "tab_audio"
                    ? "bg-blue-50 border-blue-300 text-blue-700 font-bold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                💻 Google Meet Tab Audio
              </button>
              <button
                type="button"
                disabled={capturing}
                onClick={() => setAudioSource("browser_mic")}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center gap-1.5 ${
                  audioSource === "browser_mic"
                    ? "bg-blue-50 border-blue-300 text-blue-700 font-bold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                🎙️ Browser Microphone
              </button>
              <button
                type="button"
                onClick={() => setShowVbGuide((prev) => !prev)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-slate-700 border border-slate-200 hover:bg-slate-50 flex items-center gap-1"
              >
                <HelpCircle size={13} /> VB-Cable Setup
              </button>
            </div>
          </div>

          {/* Status badge for VB-Cable */}
          {audioSource === "vb_cable" && (
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-slate-600">
                <strong>VB-Cable Device:</strong>{" "}
                {vbDeviceInfo?.vb_cable_name
                  ? `${vbDeviceInfo.vb_cable_name} (Index #${vbDeviceInfo.vb_cable_index})`
                  : "CABLE Output (or Default Input)"}
              </span>
              {capturing ? (
                <span className="text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle2 size={13} /> Listening to both Google Meet speakers
                  {vbCaptureStatus?.chunks_processed > 0 && ` (${vbCaptureStatus.chunks_processed} chunks processed)`}
                </span>
              ) : (
                <span className="text-slate-500">Ready to start capturing Google Meet candidate & interviewer audio</span>
              )}
            </div>
          )}

          {/* Collapsible Setup Guide */}
          {showVbGuide && (
            <div className="p-3 bg-blue-50/60 border border-blue-200 rounded-lg text-xs text-slate-700 space-y-2">
              <p className="font-bold text-blue-900">Windows VB-Audio Cable Setup Guide (for Google Meet):</p>
              <ol className="list-decimal list-inside space-y-1 text-slate-600">
                <li>
                  <strong>Install VB-Cable:</strong> Download free from{" "}
                  <a href="https://vb-audio.com/Cable/" target="_blank" rel="noreferrer" className="text-blue-600 underline font-semibold">
                    vb-audio.com/Cable
                  </a>{" "}
                  and install.
                </li>
                <li>
                  <strong>Route meeting audio:</strong> Open Windows Sound Settings → Set <strong>CABLE Input</strong> as default playback device.
                </li>
                <li>
                  <strong>Hear your speakers:</strong> Right-click <strong>CABLE Output</strong> → Properties → Listen tab → check{" "}
                  <strong>✅ Listen to this device</strong> → Select your headphones/speakers.
                </li>
                <li>
                  <strong>Start Sherlock:</strong> Click <em>Start Capture</em> above. Sherlock Python backend will automatically listen to <strong>CABLE Output</strong>!
                </li>
              </ol>
            </div>
          )}
        </div>

        {/* ── Permission error ───────────────────────────────────────────── */}
        {permError && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            <AlertTriangle size={16} className="flex-shrink-0" />
            {permError} — <a href="chrome://settings/content/microphone" className="underline font-semibold">Open settings</a>
          </div>
        )}

        {/* ── Capture status pills ───────────────────────────────────────── */}
        {capturing && (
          <div className="flex gap-2 flex-wrap">
            <Pill on={micOn} onLabel="Mic Live" offLabel="Mic Off" icon={Mic} offIcon={MicOff} />
            <Pill on={camOn} onLabel="Camera Live" offLabel="Camera Off" icon={Video} offIcon={VideoOff} />
            <span className="text-xs text-slate-500 self-center">
              Audio sent every {AUDIO_INTERVAL / 1000}s · Video frame every {VIDEO_INTERVAL / 1000}s
            </span>
          </div>
        )}

        {/* ── Stats row ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Confidence" value={`${confidence}%`} sub={riskLabel} icon={ShieldCheck} color="text-blue-600" />
          <StatCard label="Evidence Events" value={evidenceCount} sub="AI signals collected" icon={FileText} color="text-purple-600" />
          <StatCard label="Transcript Segments" value={transcriptCount} sub="Spoken entries" icon={Mic} color="text-emerald-600" />
          <StatCard label="Timeline Points" value={timelineCount} sub="Snapshots recorded" icon={TrendingUp} color="text-amber-600" />
        </div>

        {/* ── Main grid ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">

          {/* Left: Gauge + Webcam preview + Upload log */}
          <div className="space-y-4">

            {/* Confidence Gauge */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col items-center gap-3">
              <div className="flex items-center justify-between w-full">
                <h3 className="font-semibold text-slate-700 text-sm flex items-center gap-2">
                  <ShieldCheck size={15} className="text-blue-600" />
                  Identity Confidence
                </h3>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${riskCls}`}>
                  {riskLabel}
                </span>
              </div>
              <Gauge pct={confidence} />
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div className="h-2 rounded-full transition-all duration-700"
                  style={{ width: `${confidence}%`, backgroundColor: confidence >= 75 ? "#10b981" : confidence >= 50 ? "#f59e0b" : "#ef4444" }} />
              </div>
            </div>

            {/* Webcam preview */}
            <div className="bg-slate-900 rounded-xl overflow-hidden aspect-video relative">
              <video ref={videoRef} autoPlay muted playsInline
                className="w-full h-full object-cover" />
              {!camOn && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 gap-2">
                  <VideoOff size={32} />
                  <p className="text-xs font-medium">{capturing ? "Camera access denied" : "Click Start Capture"}</p>
                </div>
              )}
              {camOn && (
                <div className="absolute top-2 left-2 flex items-center gap-1.5 bg-red-600 text-white px-2 py-0.5 rounded text-[10px] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" /> LIVE
                </div>
              )}
            </div>

            {/* Upload activity log */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
              <h3 className="font-semibold text-slate-700 text-sm mb-2 flex items-center gap-2">
                <UploadCloud size={14} className="text-blue-600" />
                Capture Activity
              </h3>
              <div className="max-h-48 overflow-y-auto space-y-0.5">
                {uploadLog.length === 0 ? (
                  <p className="text-xs text-slate-400 py-2 text-center">No activity yet — click Start Capture</p>
                ) : (
                  uploadLog.map((e, i) => <LogEntry key={i} entry={e} />)
                )}
              </div>
            </div>
          </div>

          {/* Right: Timeline + Explanations + Transcript */}
          <div className="xl:col-span-2 space-y-4">

            {/* Confidence Timeline */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h3 className="font-semibold text-slate-700 text-sm mb-3 flex items-center gap-2">
                <TrendingUp size={15} className="text-blue-600" />
                Confidence Timeline
                <span className="ml-auto text-xs text-slate-400">{timelineCount} points</span>
              </h3>
              {timeline.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-6">Upload audio/video to generate timeline data</p>
              ) : (
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {[...timeline].reverse().slice(0, 20).map((t, i) => {
                    const pct = Math.round((t.confidence ?? 0) * 100);
                    const color = pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-500" : "bg-red-500";
                    return (
                      <div key={i} className="flex items-center gap-3 text-xs">
                        <span className="text-slate-400 w-20 flex-shrink-0">
                          {t.created_at ? new Date(t.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "--"}
                        </span>
                        <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className={`h-2 rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="w-10 text-right font-semibold text-slate-700">{pct}%</span>
                        <span className="text-slate-400 truncate w-32">{t.evidence_type ?? ""}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* AI Explanations */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h3 className="font-semibold text-slate-700 text-sm mb-3 flex items-center gap-2">
                <FileText size={15} className="text-purple-600" />
                AI Reasoning
                <span className="ml-auto text-xs text-slate-400">{evidenceCount} events</span>
              </h3>
              <div className="space-y-2 max-h-52 overflow-y-auto">
                {explanations.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-4">AI analysis will appear here as audio/video is processed</p>
                ) : (
                  [...explanations].reverse().slice(0, 10).map((e, i) => (
                    <div key={i} className="flex items-start gap-2 p-2.5 bg-slate-50 rounded-lg text-xs border border-slate-100">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${
                        (e.confidence_delta ?? 0) >= 0 ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}>
                        {e.evidence_type ?? e.evidence_label ?? "signal"}
                      </span>
                      <span className="text-slate-600 leading-relaxed">{e.explanation}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Transcript */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-slate-700 text-sm flex items-center gap-2">
                  <Mic size={15} className="text-emerald-600" />
                  Live Transcript
                  <span className="text-xs text-slate-400 font-normal">({transcriptCount} segments)</span>
                </h3>
                <button
                  onClick={handleResetSession}
                  className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center gap-1 transition"
                >
                  <RotateCcw size={12} /> Clear
                </button>
              </div>
              <div className="space-y-2 max-h-52 overflow-y-auto">
                {transcripts.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-4">Transcript will appear here after each audio chunk is processed</p>
                ) : (
                  [...transcripts].reverse().slice(0, 15).map((t, i) => (
                    <div key={i} className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-xs">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-semibold text-blue-700 capitalize">{t.speaker ?? "candidate"}</span>
                        <span className="text-slate-400">
                          {t.confidence ? `${Math.round(t.confidence * 100)}% confidence` : ""}
                        </span>
                      </div>
                      <p className="text-slate-700 leading-relaxed">{t.text}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
