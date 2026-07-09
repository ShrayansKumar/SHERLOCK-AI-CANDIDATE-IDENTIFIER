/**
 * Reusable drag-and-drop upload card with progress bar.
 * Props:
 *   accept        — string e.g. ".mp4,.webm"
 *   label         — heading label
 *   description   — subtitle
 *   icon          — lucide icon component
 *   file          — currently selected File or null
 *   onFile        — callback(File)
 *   onClear       — callback()
 *   uploading     — bool
 *   uploadPct     — 0-100 (null = indeterminate)
 *   onSubmit      — async callback()
 *   error         — string or null
 */
import { useRef, useState } from "react";
import { Upload, CheckCircle2, AlertCircle, Loader2, X } from "lucide-react";

export default function UploadCard({
  accept,
  label,
  description,
  icon: Icon,
  file,
  onFile,
  onClear,
  uploading,
  uploadPct,
  onSubmit,
  error,
}) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    onFile?.(e.dataTransfer.files[0]);
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          dragging
            ? "border-blue-400 bg-blue-50"
            : file
            ? "border-emerald-400 bg-emerald-50"
            : "border-slate-300 bg-white hover:border-blue-300"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => onFile?.(e.target.files[0])}
        />

        {file ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle2 size={40} className="text-emerald-500" />
            <p className="font-semibold text-slate-800">{file.name}</p>
            <p className="text-sm text-slate-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onClear?.(); }}
              className="mt-1 flex items-center gap-1 text-xs text-red-500 hover:text-red-700"
            >
              <X size={12} /> Remove
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            {Icon ? (
              <Icon size={40} className="text-slate-400" />
            ) : (
              <Upload size={40} className="text-slate-400" />
            )}
            <div>
              <p className="font-semibold text-slate-700">{label}</p>
              <p className="text-sm text-slate-400 mt-0.5">{description}</p>
            </div>
          </div>
        )}
      </div>

      {/* Upload progress bar */}
      {uploading && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-slate-500">
            <span>Uploading &amp; processing…</span>
            {uploadPct != null && <span>{uploadPct}%</span>}
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
            {uploadPct != null ? (
              <div
                className="h-2.5 bg-blue-500 rounded-full transition-all duration-300"
                style={{ width: `${uploadPct}%` }}
              />
            ) : (
              // Indeterminate
              <div className="h-2.5 bg-blue-500 rounded-full w-1/3 animate-[shimmer_1.2s_ease-in-out_infinite]" />
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* Submit button */}
      <button
        type="button"
        onClick={onSubmit}
        disabled={!file || uploading}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {uploading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Processing…
          </>
        ) : (
          <>
            <Upload size={18} />
            Upload &amp; Analyse
          </>
        )}
      </button>
    </div>
  );
}
