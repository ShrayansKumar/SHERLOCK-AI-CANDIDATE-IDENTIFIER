function ParticipantCard({ participant }) {
  const confPct = Math.round((participant.confidence ?? 0.8) * 100);
  const confColor =
    confPct >= 80
      ? "bg-emerald-100 text-emerald-800"
      : confPct >= 60
      ? "bg-amber-100 text-amber-800"
      : "bg-red-100 text-red-800";

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-800">
          {participant.display_name}
        </h3>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${confColor}`}>
          {confPct}% Confidence
        </span>
      </div>

      <p className="text-sm text-slate-500 mt-2">
        Role: <span className="font-semibold text-blue-700">{participant.role}</span>
      </p>

      <p className="text-sm text-slate-500">
        Email: {participant.email || "N/A"}
      </p>

      <div className="mt-4 flex items-center gap-2">
        <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm capitalize">
          {participant.status}
        </span>
      </div>
    </div>
  );
}

export default ParticipantCard;