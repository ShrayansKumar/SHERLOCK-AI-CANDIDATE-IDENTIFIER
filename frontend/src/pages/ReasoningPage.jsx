import React from "react";
import MainLayout from "../components/layout/MainLayout";
import ExplanationPanel from "../components/explanation/ExplanationPanel";
import useExplanation from "../hooks/useExplanation";
import useParticipants from "../hooks/useParticipants";
import {
  BrainCircuit,
  Cpu,
  Layers,
  Scale,
  ShieldCheck,
  AlertTriangle,
  Mic,
  Video,
  FileText,
  UserCheck,
} from "lucide-react";

const CANDIDATE = "candidate_001";

const REASONING_WEIGHTS = [
  {
    category: "Voice & Speech Analysis",
    icon: Mic,
    signals: [
      { name: "Speaker Diarization Match", weight: "+0.20", impact: "positive" },
      { name: "Long Silence / Unresponsive", weight: "-0.10", impact: "negative" },
      { name: "Voice Embedding Drift", weight: "-0.25", impact: "negative" },
    ],
  },
  {
    category: "Video & Vision Intelligence",
    icon: Video,
    signals: [
      { name: "Continuous Face Detected", weight: "+0.05", impact: "positive" },
      { name: "Eye Contact Maintained", weight: "+0.08", impact: "positive" },
      { name: "Multiple Faces Detected", weight: "-0.35", impact: "negative" },
      { name: "Identity Face Inconsistency", weight: "-0.30", impact: "negative" },
      { name: "Suspicious Background OCR", weight: "-0.15", impact: "negative" },
    ],
  },
  {
    category: "Display Name & Metadata Rules",
    icon: UserCheck,
    signals: [
      { name: "Exact Display Name Match", weight: "+0.10", impact: "positive" },
      { name: "Similar Candidate Name", weight: "+0.05", impact: "positive" },
      { name: "Unknown / Wrong Display Name", weight: "-0.15", impact: "negative" },
    ],
  },
];

export default function ReasoningPage() {
  const { participants } = useParticipants();
  const activeCandidate = participants?.[0]?.participant_id || CANDIDATE;
  const { explanations, loading } = useExplanation(activeCandidate);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <BrainCircuit className="text-blue-600" size={32} />
              AI Reasoning Engine
            </h1>
            <p className="text-slate-500 mt-1">
              Multimodal Bayesian update model and real-time evidence explainability pipeline.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg text-sm text-blue-800 font-medium">
            <Cpu size={16} />
            Bayesian Fusion Pipeline Active
          </div>
        </div>

        {/* Top Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2.5 text-blue-600 font-semibold text-sm">
              <Layers size={18} />
              Multimodal Integration
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              Combines independent signals from audio Whisper transcripts, video face tracking, and WebRTC metadata into a unified confidence metric.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2.5 text-emerald-600 font-semibold text-sm">
              <Scale size={18} />
              Dynamic Bayesian Updates
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              Each detected event applies a probabilistic positive or negative delta to the candidate identity confidence snapshot in real time.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
            <div className="flex items-center gap-2.5 text-purple-600 font-semibold text-sm">
              <ShieldCheck size={18} />
              Explainable AI (XAI)
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              Every confidence shift generates an auditable, human-readable rationale log explaining precisely why identity trust changed.
            </p>
          </div>
        </div>

        {/* Explanation Panel from backend */}
        <ExplanationPanel explanations={explanations} loading={loading} />

        {/* Evidence Weight Matrix */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-slate-800">
              Sherlock AI Evidence Matrix & Weights
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Pre-configured Bayesian confidence adjustments applied when multimodal events occur.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {REASONING_WEIGHTS.map((cat, idx) => {
              const Icon = cat.icon;
              return (
                <div
                  key={idx}
                  className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 space-y-3"
                >
                  <div className="flex items-center gap-2.5 font-semibold text-slate-800 text-sm">
                    <Icon size={18} className="text-blue-600" />
                    {cat.category}
                  </div>
                  <div className="space-y-2">
                    {cat.signals.map((sig, sIdx) => (
                      <div
                        key={sIdx}
                        className="flex items-center justify-between text-xs bg-white px-3 py-2.5 rounded-lg border border-slate-100 shadow-2xs"
                      >
                        <span className="text-slate-700 font-medium">{sig.name}</span>
                        <span
                          className={`font-mono font-bold px-2 py-0.5 rounded ${
                            sig.impact === "positive"
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : "bg-red-50 text-red-700 border border-red-200"
                          }`}
                        >
                          {sig.weight}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
