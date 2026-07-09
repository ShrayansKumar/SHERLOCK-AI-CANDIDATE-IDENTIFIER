import { useState } from "react";
import { Video, CheckCircle2 } from "lucide-react";
import { uploadVideo } from "../services/videoService";
import MainLayout from "../components/layout/MainLayout";
import UploadCard from "../components/upload/UploadCard";

const PARTICIPANT_ID = "candidate_001";
const MEETING_ID = "1";

function EvidenceBadge({ label }) {
  const colorMap = {
    camera_on:                    "bg-emerald-100 text-emerald-700",
    camera_off:                   "bg-red-100 text-red-700",
    speaking:                     "bg-sky-100 text-sky-700",
    screen_share_without_speaking:"bg-amber-100 text-amber-700",
  };
  const cls = colorMap[label] ?? "bg-slate-100 text-slate-600";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="bg-slate-50 rounded-lg p-3 text-center">
      <p className="text-lg font-bold text-slate-800">{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  );
}

export default function VideoUploadPage() {
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadPct, setUploadPct] = useState(null);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);

  const handleFile = (f) => {
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["mp4", "webm", "mov", "avi", "mkv"].includes(ext)) {
      setError("Only .mp4, .webm, .mov, .avi, and .mkv files are supported.");
      return;
    }
    setFile(f);
    setResult(null);
    setError(null);
  };

  const handleClear = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setUploadPct(null);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    setUploadPct(0);
    try {
      const data = await uploadVideo(PARTICIPANT_ID, MEETING_ID, file, (pct) => {
        setUploadPct(pct);
      });
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Upload failed.");
    } finally {
      setUploading(false);
      setUploadPct(null);
    }
  };

  const pct = result ? Math.round((result.confidence ?? 0) * 100) : null;

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Video className="text-violet-500" size={30} />
            Video Upload
          </h1>
          <p className="text-slate-500 mt-1">
            Upload a candidate interview video. Sherlock will analyse camera presence,
            screen-share activity, and speaking signals to update the confidence score.
          </p>
        </div>

        {/* Upload Card */}
        <UploadCard
          accept=".mp4,.webm,.mov,.avi,.mkv"
          label="Drop your video file here"
          description="or click to browse — MP4, WebM, MOV, AVI, MKV supported"
          icon={Video}
          file={file}
          onFile={handleFile}
          onClear={handleClear}
          uploading={uploading}
          uploadPct={uploadPct}
          onSubmit={handleSubmit}
          error={error}
        />

        {/* Result */}
        {result && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
            <div className="flex items-center gap-3">
              <CheckCircle2 size={24} className="text-emerald-500 flex-shrink-0" />
              <div>
                <h2 className="text-lg font-semibold text-slate-800">Analysis Complete</h2>
                <p className="text-sm text-slate-500">{result.file_name}</p>
              </div>
              <div className="ml-auto text-right">
                <p className="text-3xl font-bold text-violet-700">{pct}%</p>
                <p className="text-xs text-slate-400">confidence</p>
              </div>
            </div>

            {/* Confidence bar */}
            <div className="w-full bg-slate-200 rounded-full h-2.5">
              <div
                className="h-2.5 rounded-full transition-all duration-700"
                style={{
                  width: `${pct}%`,
                  backgroundColor: pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444",
                }}
              />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <StatBox label="Duration" value={result.duration ? `${result.duration.toFixed(1)}s` : "N/A"} />
              <StatBox label="Frames Sampled" value={result.frame_count ?? 0} />
              <StatBox label="Format" value={result.file_format?.toUpperCase() ?? "—"} />
            </div>

            {/* Analysis breakdown */}
            {result.analysis && Object.keys(result.analysis).length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-600 mb-2">Frame Analysis</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {result.analysis.camera_active_ratio != null && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-emerald-700">
                        {Math.round(result.analysis.camera_active_ratio * 100)}%
                      </p>
                      <p className="text-xs text-emerald-600">Camera Active</p>
                    </div>
                  )}
                  {result.analysis.screen_share_ratio != null && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-amber-700">
                        {Math.round(result.analysis.screen_share_ratio * 100)}%
                      </p>
                      <p className="text-xs text-amber-600">Screen Share</p>
                    </div>
                  )}
                  {result.analysis.black_frame_ratio != null && (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-slate-700">
                        {Math.round(result.analysis.black_frame_ratio * 100)}%
                      </p>
                      <p className="text-xs text-slate-500">Camera Off</p>
                    </div>
                  )}
                </div>
                {result.analysis.note && (
                  <p className="mt-2 text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg p-2">
                    ⚠ {result.analysis.note}
                  </p>
                )}
              </div>
            )}

            {/* Evidence */}
            {result.evidence_generated?.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-600 mb-2">Evidence Generated</p>
                <div className="flex flex-wrap gap-2">
                  {result.evidence_generated.map((ev) => (
                    <EvidenceBadge key={ev} label={ev} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
