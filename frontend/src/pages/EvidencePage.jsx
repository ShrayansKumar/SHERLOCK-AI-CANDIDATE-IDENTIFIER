import React, { useState } from "react";
import MainLayout from "../components/layout/MainLayout";
import useExplanation from "../hooks/useExplanation";
import useParticipants from "../hooks/useParticipants";
import { FileText, Filter, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";

const CANDIDATE = "candidate_001";

export default function EvidencePage() {
  const { participants } = useParticipants();
  const activeCandidate = participants?.[0]?.participant_id || CANDIDATE;
  const { explanations, loading, error } = useExplanation(activeCandidate);
  const [filterType, setFilterType] = useState("all"); // "all" | "positive" | "negative"

  // Classify positive vs negative evidence types based on standard naming or text
  const isPositive = (item) => {
    const t = (item.evidence_type || "").toLowerCase();
    const e = (item.explanation || "").toLowerCase();
    if (t.includes("match") || t.includes("on") || t.includes("speaking") || t.includes("maintained") || t.includes("positive") || e.includes("verified") || e.includes("match")) {
      return true;
    }
    return false;
  };

  const filtered = (explanations || []).filter((item) => {
    if (filterType === "positive") return isPositive(item);
    if (filterType === "negative") return !isPositive(item);
    return true;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <FileText className="text-blue-600" size={32} />
              Auditable Evidence Logs
            </h1>
            <p className="text-slate-500 mt-1">
              Immutable log of all detected multimodal signals and AI reasoning justifications.
            </p>
          </div>

          {/* Filter tabs */}
          <div className="flex items-center gap-1 bg-slate-100 p-1.5 rounded-lg border border-slate-200 text-sm font-medium">
            <button
              onClick={() => setFilterType("all")}
              className={`px-3 py-1.5 rounded-md transition-all ${
                filterType === "all"
                  ? "bg-white text-slate-800 shadow-2xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              All ({explanations?.length || 0})
            </button>
            <button
              onClick={() => setFilterType("positive")}
              className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
                filterType === "positive"
                  ? "bg-white text-emerald-700 shadow-2xs"
                  : "text-slate-600 hover:text-emerald-700"
              }`}
            >
              <CheckCircle2 size={14} />
              Positive
            </button>
            <button
              onClick={() => setFilterType("negative")}
              className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
                filterType === "negative"
                  ? "bg-white text-red-700 shadow-2xs"
                  : "text-slate-600 hover:text-red-700"
              }`}
            >
              <AlertTriangle size={14} />
              Flagged
            </button>
          </div>
        </div>

        {/* Main List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          {loading ? (
            <div className="py-12 text-center text-slate-500">Loading evidence logs...</div>
          ) : error ? (
            <div className="py-8 text-center text-red-600">
              Failed to load evidence: {error.message}
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              No matching evidence entries found.
            </div>
          ) : (
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
              {filtered.map((item) => {
                const pos = isPositive(item);
                return (
                  <div
                    key={item.id}
                    className={`border-l-4 rounded-lg p-4 transition-all ${
                      pos
                        ? "border-emerald-500 bg-emerald-50/40"
                        : "border-amber-500 bg-amber-50/40"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-semibold text-sm px-2.5 py-0.5 rounded-md ${
                              pos
                                ? "bg-emerald-100 text-emerald-800"
                                : "bg-amber-100 text-amber-800"
                            }`}
                          >
                            {item.evidence_type}
                          </span>
                        </div>
                        <p className="text-slate-700 text-sm font-medium mt-2 leading-relaxed">
                          {item.explanation}
                        </p>
                      </div>

                      <div className="text-xs text-slate-400 whitespace-nowrap">
                        {item.created_at
                          ? new Date(item.created_at).toLocaleString([], {
                              dateStyle: "medium",
                              timeStyle: "short",
                            })
                          : "—"}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
