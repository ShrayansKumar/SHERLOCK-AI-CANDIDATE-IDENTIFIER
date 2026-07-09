import { useState } from "react";
import { Mic, CheckCircle2 } from "lucide-react";
import { uploadAudio } from "../services/audioService";
import MainLayout from "../components/layout/MainLayout";
import UploadCard from "../components/upload/UploadCard";

const PARTICIPANT_ID = "candidate_001";
const MEETING_ID = "1";

function EvidenceBadge({ label }) {
  const colorMap = {
    speaking:         "bg-sky-100 text-sky-700",
    long_answer:      "bg-emerald-100 text-emerald-700",
    short_answer:     "bg-amber-100 text-amber-700",
    technical_answer: "bg-violet-100 text-violet-700",
    confident_speech: "bg-green-100 text-green-700",
    long_silence:     "bg-red-100 text-red-700",
    empty_transcript: "bg-slate-100 text-slate-500",
  };
  const cls = colorMap[label] ?? "bg-slate-100 text-slate-600";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

function formatTime(s) {
  if (s == null) return "--:--";
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

export default function AudioUploadPage() {
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadPct, setUploadPct] = useState(null);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);

  const handleFile = (f) => {
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["wav", "mp3", "m4a"].includes(ext)) {
      setError("Only .wav, .mp3, and .m4a files are supported.");
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
      const data = await uploadAudio(PARTICIPANT_ID, MEETING_ID, file, (pct) => {
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
            <Mic className="text-blue-500" size={30} />
            Audio Upload
          </h1>
          <p className="text-slate-500 mt-1">
            Upload a candidate interview recording. Sherlock will transcribe it,
            generate embeddings, and update the confidence score.
          </p>
        </div>

        {/* Upload Card */}
        <UploadCard
          accept=".wav,.mp3,.m4a"
          label="Drop your audio file here"
          description="or click to browse — WAV, MP3, M4A supported"
          icon={Mic}
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
                <p className="text-3xl font-bold text-blue-700">{pct}%</p>
                <p className="text-xs text-slate-400">confidence</p>
              </div>
            </div>

            <div className="w-full bg-slate-200 rounded-full h-2.5">
              <div
                className="h-2.5 rounded-full transition-all duration-700"
                style={{
                  width: `${pct}%`,
                  backgroundColor: pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444",
                }}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: "Duration",   value: `${result.duration?.toFixed(1)}s` },
                { label: "Language",   value: result.language?.toUpperCase() ?? "—" },
                { label: "Segments",   value: result.segments?.length ?? 0 },
                { label: "Embeddings", value: result.embeddings_count ?? 0 },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-slate-800">{value}</p>
                  <p className="text-xs text-slate-400">{label}</p>
                </div>
              ))}
            </div>

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

            {result.transcript && (
              <div>
                <p className="text-sm font-semibold text-slate-600 mb-2">Full Transcript</p>
                <p className="text-sm text-slate-700 bg-slate-50 rounded-lg p-3 leading-relaxed border border-slate-100">
                  {result.transcript}
                </p>
              </div>
            )}

            {result.segments?.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-600 mb-2">Segments</p>
                <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                  {result.segments.map((seg, i) => (
                    <div key={i} className="flex gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="flex-shrink-0 w-10 text-center">
                        <span className="text-xs font-semibold text-blue-600">#{i + 1}</span>
                        <p className="text-xs text-slate-400 mt-0.5">{formatTime(seg.start)}</p>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-800 leading-relaxed">{seg.text}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          Confidence: {Math.round((seg.confidence ?? 0) * 100)}%
                        </p>
                      </div>
                    </div>
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
