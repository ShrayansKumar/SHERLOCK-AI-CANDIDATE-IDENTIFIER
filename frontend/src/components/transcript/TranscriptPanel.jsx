import { MessageSquareText, RefreshCw } from "lucide-react";

function ConfidenceBadge({ confidence }) {
  const pct = Math.round((confidence ?? 0) * 100);
  const color =
    pct >= 70
      ? "bg-emerald-100 text-emerald-700"
      : pct >= 40
      ? "bg-amber-100 text-amber-700"
      : "bg-red-100 text-red-700";
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {pct}%
    </span>
  );
}

export default function TranscriptPanel({ transcripts, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <MessageSquareText size={22} />
          Transcript
        </h2>
        <div className="mt-4 space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse space-y-2">
              <div className="h-3 bg-slate-200 rounded w-1/4" />
              <div className="h-4 bg-slate-100 rounded w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!transcripts || transcripts.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <Header onRefresh={onRefresh} />
        <p className="mt-4 text-slate-500 text-sm">
          No transcript segments available. Upload an audio file to see results.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <Header onRefresh={onRefresh} count={transcripts.length} />

      <div className="mt-4 max-h-[420px] overflow-y-auto pr-2 space-y-3">
        {transcripts.map((seg, i) => (
          <div
            key={seg.id ?? i}
            className="flex gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100 hover:border-blue-200 transition-colors"
          >
            {/* Time stamp pill */}
            <div className="flex-shrink-0 w-[72px] text-center">
              <span className="inline-block text-xs font-mono bg-slate-200 text-slate-600 px-2 py-0.5 rounded-md">
                {formatTime(seg.start)}
              </span>
              <span className="block text-xs text-slate-400 mt-0.5">→</span>
              <span className="inline-block text-xs font-mono bg-slate-200 text-slate-600 px-2 py-0.5 rounded-md">
                {formatTime(seg.end)}
              </span>
            </div>

            {/* Text */}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-800 leading-relaxed">
                {seg.text}
              </p>
              <div className="flex items-center gap-2 mt-1.5">
                {seg.confidence != null && (
                  <ConfidenceBadge confidence={seg.confidence} />
                )}
                {seg.speaker && (
                  <span className="text-xs text-slate-400">
                    {seg.speaker}
                  </span>
                )}
                {seg.created_at && (
                  <span className="text-xs text-slate-400 ml-auto">
                    {new Date(seg.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Header({ onRefresh, count }) {
  return (
    <div className="flex items-center justify-between">
      <h2 className="text-xl font-semibold flex items-center gap-2">
        <MessageSquareText size={22} />
        Transcript
        {count != null && (
          <span className="ml-1 text-sm font-normal text-slate-400">
            ({count} segments)
          </span>
        )}
      </h2>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600 transition-colors"
          title="Refresh transcript"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      )}
    </div>
  );
}

function formatTime(seconds) {
  if (seconds == null) return "--:--";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}
