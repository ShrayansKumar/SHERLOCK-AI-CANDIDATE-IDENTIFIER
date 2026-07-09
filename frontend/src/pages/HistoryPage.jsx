import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import { getMeetingHistory, deleteMeeting } from "../services/meetingService";
import {
  History,
  Video,
  Users,
  Calendar,
  FileText,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Radio,
  Trash2,
} from "lucide-react";

function StatusBadge({ status }) {
  const cfg = {
    live: { cls: "bg-red-100 text-red-700 border-red-200", icon: Radio, label: "Live" },
    completed: { cls: "bg-emerald-100 text-emerald-700 border-emerald-200", icon: CheckCircle2, label: "Completed" },
    scheduled: { cls: "bg-blue-100 text-blue-700 border-blue-200", icon: Clock, label: "Scheduled" },
  }[status] ?? { cls: "bg-slate-100 text-slate-600 border-slate-200", icon: AlertCircle, label: status };

  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-semibold ${cfg.cls}`}>
      <Icon size={11} />
      {cfg.label}
    </span>
  );
}

const PLATFORM_ICONS = {
  "Google Meet": "🎥",
  "Microsoft Teams": "💼",
  "Zoom": "🔵",
};

export default function HistoryPage() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMeetingHistory();
      setSessions(data || []);
    } catch (err) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (id) => {
    if (!window.confirm("Are you sure you want to delete this interview session detail?")) return;
    try {
      await deleteMeeting(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      alert("Failed to delete session.");
    }
  };

  useEffect(() => { fetchHistory(); }, []);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <History className="text-blue-600" size={28} />
              Interview History
            </h1>
            <p className="text-slate-500 mt-1 text-sm">
              All previous and active interview sessions. Select any session to view its report.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchHistory}
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50"
            >
              <RefreshCw size={14} /> Refresh
            </button>
            <button
              onClick={() => navigate("/new-interview")}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm"
            >
              <Play size={14} /> New Interview
            </button>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center gap-3 text-slate-500 p-8">
            <RefreshCw size={20} className="animate-spin" />
            Loading interview history...
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            <p className="font-semibold">Failed to load history</p>
            <p className="mt-1">{error}</p>
            <button onClick={fetchHistory} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">
              Retry
            </button>
          </div>
        ) : sessions.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center">
            <History size={40} className="text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">No interviews yet</p>
            <p className="text-slate-400 text-sm mt-1 mb-6">
              Create your first interview session to get started.
            </p>
            <button
              onClick={() => navigate("/new-interview")}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 shadow-sm"
            >
              <Play size={16} /> Start Your First Interview
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  {["Platform", "Candidate", "Job Role", "Date & Time", "Status", "Actions"].map((h) => (
                    <th key={h} className="text-left px-5 py-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50 transition">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2 font-medium text-slate-700">
                        <span>{PLATFORM_ICONS[s.platform] ?? "📹"}</span>
                        {s.platform}
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5 font-mono">{s.meeting_id}</p>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <Users size={14} className="text-slate-400" />
                        <span className="text-slate-700 font-medium">
                          {s.candidate_name || <span className="italic text-slate-400">Unknown</span>}
                        </span>
                      </div>
                      {s.candidate_email && (
                        <p className="text-xs text-slate-400 mt-0.5">{s.candidate_email}</p>
                      )}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {s.job_role || <span className="italic text-slate-400">—</span>}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1.5 text-slate-600">
                        <Calendar size={13} className="text-slate-400" />
                        {new Date(s.created_at).toLocaleDateString()}
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {new Date(s.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={s.status} />
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex gap-2">
                        {s.status === "live" && (
                          <button
                            onClick={() => navigate(`/live/${s.id}`)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
                          >
                            <Radio size={11} /> Resume
                          </button>
                        )}
                        <button
                          onClick={() => navigate(`/report`)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold hover:bg-slate-200 transition"
                        >
                          <FileText size={11} /> Report
                        </button>
                        <button
                          onClick={() => handleDeleteSession(s.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-600 border border-red-200 rounded-lg text-xs font-semibold hover:bg-red-100 transition"
                          title="Delete Session"
                        >
                          <Trash2 size={13} /> Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
