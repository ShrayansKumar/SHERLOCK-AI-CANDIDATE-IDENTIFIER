import { useState, useCallback } from "react";
import MainLayout from "../components/layout/MainLayout";
import MeetingCard from "../components/meeting/MeetingCard";
import ParticipantsPanel from "../components/participants/ParticipantsPanel";
import ConfidenceCard from "../components/confidence/ConfidenceCard";
import ExplanationPanel from "../components/explanation/ExplanationPanel";
import ConfidenceTimeline from "../components/confidence/ConfidenceTimeline";
import TranscriptPanel from "../components/transcript/TranscriptPanel";
import useExplanation from "../hooks/useExplanation";
import useMeetings from "../hooks/useMeetings";
import useParticipants from "../hooks/useParticipants";
import useConfidence from "../hooks/useConfidence";
import useTimeline from "../hooks/useTimeline";
import useTranscript from "../hooks/useTranscript";
import useWebSocket from "../hooks/useWebSocket";
import { Wifi, WifiOff } from "lucide-react";

const CANDIDATE = "candidate_001";
const MEETING_ID = 1;

function WsIndicator({ connected }) {
  return (
    <div
      className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full ${
        connected
          ? "bg-emerald-100 text-emerald-700"
          : "bg-slate-100 text-slate-500"
      }`}
      title={connected ? "Live WebSocket connected" : "WebSocket disconnected"}
    >
      {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
      {connected ? "Live" : "Offline"}
    </div>
  );
}

function Dashboard() {
  const { meetings, loading: meetingsLoading, error: meetingsError } = useMeetings();
  const { participants, loading: participantsLoading, error: participantsError } = useParticipants();

  const activeMeetingId = meetings?.[0]?.meeting_id || meetings?.[0]?.id || MEETING_ID;
  const activeCandidate = participants?.[0]?.participant_id || meetings?.[0]?.candidate_email || CANDIDATE;

  const {
    confidence,
    loading: confidenceLoading,
    error: confidenceError,
    refresh: refreshConfidence,
  } = useConfidence(activeMeetingId);

  const {
    explanations,
    loading: explanationLoading,
    error: explanationError,
    refresh: refreshExplanations,
  } = useExplanation(activeCandidate);

  const {
    timeline,
    loading: timelineLoading,
    error: timelineError,
    refresh: refreshTimeline,
  } = useTimeline(activeCandidate);

  const {
    transcripts,
    loading: transcriptLoading,
    refresh: refreshTranscripts,
  } = useTranscript(activeCandidate);

  // ── Live WebSocket ──────────────────────────────────────────────────────────
  const handleConfidence = useCallback(() => {
    refreshConfidence();
    refreshTimeline();
  }, [refreshConfidence, refreshTimeline]);

  const handleEvidence = useCallback(() => {
    refreshExplanations();
  }, [refreshExplanations]);

  const handleTranscript = useCallback(() => {
    refreshTranscripts();
  }, [refreshTranscripts]);

  const { connected } = useWebSocket({
    onConfidence: handleConfidence,
    onEvidence:   handleEvidence,
    onTranscript: handleTranscript,
  });
  // ───────────────────────────────────────────────────────────────────────────

  const loading =
    meetingsLoading || participantsLoading || confidenceLoading || timelineLoading;

  const error =
    meetingsError || participantsError || confidenceError ||
    explanationError || timelineError;

  if (loading) {
    return (
      <MainLayout>
        <h2 className="text-xl font-semibold">Loading Sherlock AI Dashboard...</h2>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="text-red-600 text-lg">Failed to load dashboard.</div>
        <p className="mt-2">
          {meetingsError?.message ||
            participantsError?.message ||
            confidenceError?.message ||
            explanationError?.message ||
            timelineError?.message}
        </p>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
          </div>
          <WsIndicator connected={connected} />
        </div>

        {/* Row 1 – Meeting + Confidence */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <MeetingCard meeting={meetings[0]} />
          <ConfidenceCard confidence={confidence} loading={confidenceLoading} activeCandidate={activeCandidate} />
        </div>

        {/* Row 2 – Participants + Explanation */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ParticipantsPanel participants={participants} />
          <ExplanationPanel explanations={explanations} loading={explanationLoading} />
        </div>

        {/* Row 3 – Transcript */}
        <TranscriptPanel
          transcripts={transcripts}
          loading={transcriptLoading}
          onRefresh={refreshTranscripts}
        />

        {/* Row 4 – Confidence Timeline */}
        <ConfidenceTimeline timeline={timeline} loading={timelineLoading} />

      </div>
    </MainLayout>
  );
}

export default Dashboard;