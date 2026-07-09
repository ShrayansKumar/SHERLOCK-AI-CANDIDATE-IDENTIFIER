import { useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import { createMeeting, startInterview } from "../services/meetingService";
import {
  Video,
  User,
  Mail,
  Briefcase,
  Clock,
  Link2,
  Play,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

const PLATFORMS = ["Google Meet", "Microsoft Teams", "Zoom", "Other"];

function Field({ label, icon: Icon, children }) {
  return (
    <div className="space-y-1.5">
      <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
        {Icon && <Icon size={15} className="text-slate-400" />}
        {label}
      </label>
      {children}
    </div>
  );
}

const inputCls =
  "w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-slate-400 transition";

export default function NewInterviewPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    platform: "Google Meet",
    meeting_id: "",
    meeting_link: "",
    candidate_name: "",
    candidate_email: "",
    job_role: "",
    interviewer_names: "",
    expected_duration_minutes: 60,
  });

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleStart = async (e) => {
    e.preventDefault();
    if (!form.meeting_id.trim()) {
      setError("Meeting ID is required.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // 1. Create meeting record
      const meeting = await createMeeting({
        meeting_id: form.meeting_id.trim(),
        platform: form.platform,
        meeting_link: form.meeting_link.trim() || null,
        candidate_name: form.candidate_name.trim() || null,
        candidate_email: form.candidate_email.trim() || null,
        job_role: form.job_role.trim() || null,
        interviewer_names: form.interviewer_names.trim() || null,
        expected_duration_minutes: Number(form.expected_duration_minutes) || 60,
      });
      // 2. Start the interview session (sets status='live', records session_start)
      await startInterview(meeting.id);
      // 3. Navigate to live dashboard for this session
      navigate(`/live/${meeting.id}`);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : err?.message || "Failed to create interview session."
      );
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Play className="text-blue-600" size={28} />
            New Interview
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            Fill in the interview details below, then click Start Interview to begin live analysis.
          </p>
        </div>

        {/* Form Card */}
        <form
          onSubmit={handleStart}
          className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-5"
        >
          {/* Platform */}
          <Field label="Meeting Platform" icon={Video}>
            <div className="flex gap-2 flex-wrap">
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, platform: p }))}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition ${
                    form.platform === p
                      ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                      : "bg-white text-slate-600 border-slate-200 hover:border-blue-400 hover:text-blue-600"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </Field>

          {/* Two-column grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Field label="Meeting ID / Room Code *" icon={Link2}>
              <input
                className={inputCls}
                placeholder="e.g. abc-defg-hij"
                value={form.meeting_id}
                onChange={set("meeting_id")}
                required
              />
            </Field>
            <Field label="Meeting Link (optional)" icon={Link2}>
              <input
                className={inputCls}
                placeholder="https://meet.google.com/..."
                value={form.meeting_link}
                onChange={set("meeting_link")}
              />
            </Field>
          </div>

          {/* Candidate */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Field label="Candidate Name (optional)" icon={User}>
              <input
                className={inputCls}
                placeholder="e.g. John Smith"
                value={form.candidate_name}
                onChange={set("candidate_name")}
              />
            </Field>
            <Field label="Candidate Email (optional)" icon={Mail}>
              <input
                type="email"
                className={inputCls}
                placeholder="john@example.com"
                value={form.candidate_email}
                onChange={set("candidate_email")}
              />
            </Field>
          </div>

          {/* Job & Duration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Field label="Job Role" icon={Briefcase}>
              <input
                className={inputCls}
                placeholder="e.g. Senior Backend Engineer"
                value={form.job_role}
                onChange={set("job_role")}
              />
            </Field>
            <Field label="Expected Duration (minutes)" icon={Clock}>
              <input
                type="number"
                min={5}
                max={240}
                className={inputCls}
                value={form.expected_duration_minutes}
                onChange={set("expected_duration_minutes")}
              />
            </Field>
          </div>

          {/* Interviewer(s) */}
          <Field label="Interviewer Name(s)" icon={User}>
            <input
              className={inputCls}
              placeholder="e.g. Sarah Chen, Mark Rivera"
              value={form.interviewer_names}
              onChange={set("interviewer_names")}
            />
          </Field>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 transition shadow-sm disabled:opacity-60 disabled:cursor-not-allowed text-base"
          >
            {loading ? (
              <>
                <span className="animate-spin border-2 border-white border-t-transparent rounded-full w-4 h-4" />
                Creating Session...
              </>
            ) : (
              <>
                <Play size={18} />
                Start Interview
              </>
            )}
          </button>
        </form>

        {/* Info card */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 flex gap-3">
          <CheckCircle2 size={18} className="flex-shrink-0 mt-0.5 text-blue-600" />
          <div>
            <p className="font-semibold">What happens next?</p>
            <p className="mt-0.5 opacity-90">
              Sherlock creates a live session, resets all AI state, and opens the Live
              Interview Dashboard where you can upload audio and video in real time and watch
              confidence scores update instantly.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
