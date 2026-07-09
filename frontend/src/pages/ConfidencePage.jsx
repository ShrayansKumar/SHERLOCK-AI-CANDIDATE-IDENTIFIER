import React from "react";
import MainLayout from "../components/layout/MainLayout";
import ConfidenceCard from "../components/confidence/ConfidenceCard";
import ConfidenceTimeline from "../components/confidence/ConfidenceTimeline";
import useConfidence from "../hooks/useConfidence";
import useTimeline from "../hooks/useTimeline";
import useExplanation from "../hooks/useExplanation";
import useMeetings from "../hooks/useMeetings";
import useParticipants from "../hooks/useParticipants";
import { Activity, ShieldCheck, TrendingUp, CheckCircle2, AlertTriangle, FileText } from "lucide-react";

const MEETING_ID = 1;
const CANDIDATE = "candidate_001";

export default function ConfidencePage() {
  const { meetings } = useMeetings();
  const { participants } = useParticipants();

  const activeMeetingId = meetings?.[0]?.meeting_id || meetings?.[0]?.id || MEETING_ID;
  const activeCandidate = participants?.[0]?.participant_id || meetings?.[0]?.candidate_email || CANDIDATE;

  const { confidence, loading: confLoading } = useConfidence(activeMeetingId);
  const { timeline, loading: timeLoading } = useTimeline(activeCandidate);
  const { explanations, loading: expLoading } = useExplanation(activeCandidate);

  const candidateEntry = confidence?.find((c) => c.participant_id === activeCandidate) || confidence?.[0];
  const currentVal = candidateEntry?.confidence ?? 0.8;
  const currentPct = Math.round(currentVal * 100);

  // Derive stats from timeline or snapshots
  const allVals = (timeline || []).map((t) => Math.round((t.confidence ?? 0.8) * 100));
  const peak = allVals.length > 0 ? Math.max(...allVals, currentPct) : currentPct;
  const avg =
    allVals.length > 0
      ? Math.round(allVals.reduce((a, b) => a + b, 0) / allVals.length)
      : currentPct;

  const totalEv = explanations?.length || 0;
  const positiveEv = (explanations || []).filter(
    (e) => (e.evidence_type || "").includes("match") || (e.evidence_type || "").includes("maintained") || (e.evidence_type || "").includes("on")
  ).length;
  const negativeEv = totalEv - positiveEv;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <Activity className="text-blue-600" size={32} />
              Identity Confidence Monitoring
            </h1>
            <p className="text-slate-500 mt-1">
              Real-time probabilistic trust metrics and historical verification timeline.
            </p>
          </div>
        </div>

        {/* Current Completed Meeting Banner */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-emerald-100 text-emerald-800 border border-emerald-200">
                Completed Session
              </span>
              <span className="text-sm font-semibold text-slate-700">
                {meetings?.[0]?.platform || "Google Meet"} Interview
              </span>
            </div>
            <p className="text-lg font-bold text-slate-800 mt-1">
              Candidate: {meetings?.[0]?.candidate_name || participants?.[0]?.display_name || "Candidate"}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              Role: {meetings?.[0]?.job_role || "Senior Software Engineer"} · Interviewer: {meetings?.[0]?.interviewer_names || "Interviewer Panel"}
            </p>
          </div>
          <div className="flex items-center gap-4 border-t md:border-t-0 pt-3 md:pt-0 border-slate-100">
            <div className="text-right">
              <p className="text-xs text-slate-400 font-medium uppercase">Final Confidence</p>
              <p className="text-2xl font-extrabold text-emerald-600">{currentPct}%</p>
            </div>
            <span className="px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Identity Verified — Completed
            </span>
          </div>
        </div>

        {/* 6 Statistics Summary Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <ShieldCheck size={16} className="text-blue-600" />
              Current Confidence
            </div>
            <p className="text-2xl font-extrabold text-slate-800 mt-2">{currentPct}%</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <TrendingUp size={16} className="text-emerald-600" />
              Peak Confidence
            </div>
            <p className="text-2xl font-extrabold text-emerald-600 mt-2">{peak}%</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <Activity size={16} className="text-blue-500" />
              Average Confidence
            </div>
            <p className="text-2xl font-extrabold text-blue-600 mt-2">{avg}%</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <FileText size={16} className="text-slate-600" />
              Total Evidence
            </div>
            <p className="text-2xl font-extrabold text-slate-800 mt-2">{expLoading ? "..." : totalEv}</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <CheckCircle2 size={16} className="text-emerald-600" />
              Positive Evidence
            </div>
            <p className="text-2xl font-extrabold text-emerald-600 mt-2">{expLoading ? "..." : positiveEv}</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
              <AlertTriangle size={16} className="text-red-600" />
              Negative Evidence
            </div>
            <p className="text-2xl font-extrabold text-red-600 mt-2">{expLoading ? "..." : negativeEv}</p>
          </div>
        </div>

        {/* Grid Layout for Card & Timeline */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-1">
            <ConfidenceCard
              confidence={confidence}
              loading={confLoading}
              activeCandidate={activeCandidate}
              activeMeeting={meetings?.[0]}
              activeParticipant={participants?.[0]}
            />
          </div>
          <div className="xl:col-span-2">
            <ConfidenceTimeline timeline={timeline} loading={timeLoading} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
