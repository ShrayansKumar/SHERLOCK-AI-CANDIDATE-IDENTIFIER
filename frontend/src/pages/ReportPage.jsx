import { useState, useEffect, useRef } from "react";
import {
  FileText,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  TrendingUp,
  ShieldAlert,
  User,
  FileJson,
  Activity,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { getReport, exportReportJSON } from "../services/reportService";
import MainLayout from "../components/layout/MainLayout";

const PARTICIPANT_ID = "candidate_001";

function VerdictBanner({ verdict, pct, riskLevel, recommendation }) {
  const isHigh = pct >= 70;
  const isMid = pct >= 50;

  const cfg = isHigh
    ? { bg: "bg-emerald-50 border-emerald-300", icon: CheckCircle2, iconCls: "text-emerald-600", textCls: "text-emerald-800" }
    : isMid
    ? { bg: "bg-amber-50 border-amber-300", icon: AlertTriangle, iconCls: "text-amber-600", textCls: "text-amber-800" }
    : { bg: "bg-red-50 border-red-300", icon: XCircle, iconCls: "text-red-600", textCls: "text-red-800" };

  const Icon = cfg.icon;

  return (
    <div className={`flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl border ${cfg.bg}`}>
      <div className="flex items-start gap-3">
        <Icon size={28} className={`flex-shrink-0 mt-0.5 ${cfg.iconCls}`} />
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <p className={`font-bold text-xl ${cfg.textCls}`}>{verdict || "Identity Verified — Meeting Completed"}</p>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
              riskLevel === "Low Risk"
                ? "bg-emerald-200 text-emerald-900"
                : riskLevel === "Medium Risk"
                ? "bg-amber-200 text-amber-900"
                : "bg-red-200 text-red-900"
            }`}>
              Risk: {riskLevel || "Low Risk"}
            </span>
          </div>
          <p className={`text-sm ${cfg.textCls} opacity-90 mt-1 font-medium`}>
            Identity Confidence: {pct}% — Status: {verdict || (pct >= 70 ? "Identity Verified — Meeting Completed" : "Manual Review Required")}
          </p>
          {recommendation && (
            <p className={`text-xs ${cfg.textCls} opacity-80 mt-1 italic`}>
              Recommendation: {recommendation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 text-center shadow-sm">
      <p className="text-2xl font-bold text-slate-800">{value}</p>
      <p className="text-sm font-medium text-slate-600 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  );
}

function Section({ title, icon: Icon, children, className = "" }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-sm p-6 ${className}`}>
      <h3 className="text-base font-semibold text-slate-700 flex items-center gap-2 mb-4">
        {Icon && <Icon size={18} />}
        {title}
      </h3>
      {children}
    </div>
  );
}

function EvidenceBadge({ label, type, delta }) {
  const positive = delta > 0;
  return (
    <div className={`flex items-center justify-between px-3 py-2 rounded-lg border text-sm ${
      positive ? "bg-emerald-50 border-emerald-200" : "bg-red-50 border-red-200"
    }`}>
      <span className={`font-medium ${positive ? "text-emerald-800" : "text-red-800"}`}>
        {label || type.replace(/_/g, " ")}
      </span>
      <span className={`font-semibold ml-2 ${positive ? "text-emerald-700" : "text-red-700"}`}>
        {delta > 0 ? "+" : ""}{(delta * 100).toFixed(0)}%
      </span>
    </div>
  );
}

export default function ReportPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingJson, setDownloadingJson] = useState(false);
  const printRef = useRef();

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getReport(PARTICIPANT_ID);
      setReport(data);
    } catch (err) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Failed to load report.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReport(); }, []);

  const handlePrint = () => {
    window.print();
  };

  const handleExportJson = async () => {
    setDownloadingJson(true);
    try {
      await exportReportJSON(PARTICIPANT_ID);
    } catch (err) {
      alert("Failed to download JSON report");
    } finally {
      setDownloadingJson(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center gap-3 text-slate-500 p-8">
          <RefreshCw size={20} className="animate-spin" />
          Loading final evaluation report…
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="p-8 text-red-600">
          <p className="font-semibold">Failed to load report</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={fetchReport}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </MainLayout>
    );
  }

  if (!report) {
    return (
      <MainLayout>
        <div className="p-8 text-slate-500">No report data available.</div>
      </MainLayout>
    );
  }

  const {
    participant = {},
    confidence = {},
    timeline = [],
    evidence = { logs: [] },
    explanations = [],
    transcripts = [],
    audio_uploads = [],
    video_uploads = [],
    ai_summary = "",
    candidate_summary = {},
    risk_level = "Low Risk",
    verdict = {},
  } = report;

  const pct = Math.round(confidence?.percentage ?? 80);
  const chartData = (timeline || []).map((t) => ({
    time: new Date(t.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    confidence: Math.round((t.confidence ?? 0.8) * 100),
  }));

  const verdictStatus = typeof verdict === "string" ? verdict : verdict?.status || confidence?.verdict || "Identity Verified — Meeting Completed";

  return (
    <MainLayout>
      <div ref={printRef} className="max-w-5xl mx-auto space-y-6">

        {/* ── Page Header ── */}
        <div className="flex items-start justify-between print:mb-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <FileText className="text-blue-500" size={28} />
              Final Evaluation Report
            </h1>
            <p className="text-slate-500 mt-1">
              {participant?.display_name || "Candidate"} · {participant?.participant_id || "candidate_001"} · Generated {new Date().toLocaleString()}
            </p>
          </div>
          <div className="flex gap-2 print:hidden">
            <button
              onClick={fetchReport}
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50"
            >
              <RefreshCw size={14} /> Refresh
            </button>
            <button
              onClick={handleExportJson}
              disabled={downloadingJson}
              className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-700 border border-slate-300 bg-white rounded-lg hover:bg-slate-50 disabled:opacity-50"
            >
              <FileJson size={16} className="text-amber-600" />
              {downloadingJson ? "Exporting..." : "Export JSON"}
            </button>
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm"
            >
              <Download size={14} /> Export PDF
            </button>
          </div>
        </div>

        {/* ── Verdict Banner ── */}
        <VerdictBanner
          verdict={verdictStatus}
          pct={pct}
          riskLevel={risk_level}
          recommendation={verdict?.recommendation}
        />

        {/* ── AI Summary & Candidate Summary ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Section title="AI Evaluation Summary" icon={Activity} className="md:col-span-2">
            <p className="text-slate-700 text-sm leading-relaxed">
              {ai_summary || "Sherlock AI monitored the interview session and verified candidate identity signals across audio and video modalities."}
            </p>
          </Section>

          <Section title="Candidate & Meeting Summary" icon={User}>
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Name</span>
                <span className="font-bold text-slate-800">{candidate_summary?.name || participant?.display_name || "Candidate"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Email</span>
                <span className="text-slate-700">{candidate_summary?.email || participant?.email || "N/A"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Job Role</span>
                <span className="text-slate-700">{candidate_summary?.job_role || "Senior Software Engineer"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Platform</span>
                <span className="text-slate-700">{candidate_summary?.platform || "Google Meet"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Interviewer</span>
                <span className="text-slate-700">{candidate_summary?.interviewer || "Interviewer Panel"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Status</span>
                <span className="font-semibold text-emerald-700 uppercase">{candidate_summary?.meeting_status || "Completed"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Meeting ID</span>
                <span className="font-mono">{candidate_summary?.meeting_id || participant?.meeting_id || "1"}</span>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span className="font-semibold text-slate-500">Duration</span>
                <span>{candidate_summary?.interview_duration || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-slate-500">Media Files</span>
                <span>{(audio_uploads || []).length} audio · {(video_uploads || []).length} video</span>
              </div>
            </div>
          </Section>
        </div>

        {/* ── Stats Row ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Confidence Score" value={`${pct}%`} sub="Current snapshot" />
          <StatCard label="Peak Confidence" value={`${Math.round((confidence?.peak ?? 0.8) * 100)}%`} sub="Highest recorded" />
          <StatCard label="Average Confidence" value={`${Math.round((confidence?.average ?? 0.8) * 100)}%`} sub="Session average" />
          <StatCard label="Evidence Events" value={evidence?.total ?? 0} sub={`${evidence?.positive_count ?? 0} positive · ${evidence?.negative_count ?? 0} negative`} />
        </div>

        {/* ── Confidence Progress Bar ── */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between text-sm font-medium text-slate-600 mb-2">
            <span>AI Confidence Score</span>
            <span>{pct}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-4">
            <div
              className="h-4 rounded-full transition-all duration-700"
              style={{
                width: `${pct}%`,
                backgroundColor: pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444",
              }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>0% — No Confidence</span>
            <span>100% — Full Confidence</span>
          </div>
        </div>

        {/* ── Two-Column Layout (Timeline & Evidence) ── */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {chartData.length > 0 && (
            <Section title="Confidence Timeline" icon={TrendingUp} className="xl:col-span-2">
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Line
                    type="monotone"
                    dataKey="confidence"
                    stroke="#2563eb"
                    strokeWidth={2.5}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Section>
          )}

          <Section title="Evidence Breakdown" icon={CheckCircle2}>
            {!(evidence?.logs) || evidence.logs.length === 0 ? (
              <p className="text-slate-500 text-sm">No evidence recorded yet.</p>
            ) : (
              <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
                {evidence.logs.map((ev) => (
                  <EvidenceBadge
                    key={ev.id}
                    label={ev.evidence_label}
                    type={ev.evidence_type}
                    delta={ev.confidence_delta}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section title="AI Explanations" icon={FileText}>
            {!(explanations) || explanations.length === 0 ? (
              <p className="text-slate-500 text-sm">No explanations recorded yet.</p>
            ) : (
              <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
                {explanations.map((x) => (
                  <div
                    key={x.id}
                    className="border-l-4 border-blue-500 bg-slate-50 rounded-r-lg px-3 py-2"
                  >
                    <p className="text-xs font-semibold text-blue-700 mb-0.5">
                      {x.evidence_label || x.evidence_type?.replace(/_/g, " ")}
                    </p>
                    <p className="text-sm text-slate-700">{x.explanation}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {new Date(x.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Section>
        </div>

        {/* ── Transcripts ── */}
        {transcripts.length > 0 && (
          <Section title={`Transcript (${transcripts.length} segments)`} icon={FileText}>
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {transcripts.map((t) => (
                <div key={t.id} className="flex gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex-shrink-0 w-20 text-center space-y-1">
                    <span className="block text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded font-medium">
                      {t.speaker ?? "candidate"}
                    </span>
                    <span className="block text-xs text-slate-400">
                      {t.created_at
                        ? new Date(t.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                        : "—"}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed">{t.text}</p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* ── Footer on Every Page ── */}
        <div className="text-center text-xs text-slate-400 pt-6 border-t border-slate-200 mt-8 print:block">
          Generated by Sherlock AI Candidate Identifier | Version 1.0 | Confidential
        </div>
      </div>
    </MainLayout>
  );
}
