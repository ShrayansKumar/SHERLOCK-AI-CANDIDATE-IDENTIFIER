import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Dot,
} from "recharts";
import { TrendingUp, Activity } from "lucide-react";

// Customized colored dot based on confidence score or trend
const CustomColoredDot = (props) => {
  const { cx, cy, payload, index, data } = props;
  if (!cx || !cy) return null;

  // Determine trend color: Green (>= 70 or increasing), Yellow (50-69), Red (< 50 or drop)
  const prevVal = index > 0 && data ? data[index - 1]?.confidence : payload.confidence;
  const isIncreasing = payload.confidence >= prevVal;

  let fill = "#10b981"; // Green
  if (payload.confidence < 50 || (!isIncreasing && payload.confidence < 60)) {
    fill = "#ef4444"; // Red
  } else if (payload.confidence < 70) {
    fill = "#f59e0b"; // Yellow
  }

  return <circle cx={cx} cy={cy} r={5} fill={fill} stroke="#ffffff" strokeWidth={1.5} />;
};

export default function ConfidenceTimeline({ timeline, loading }) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col items-center justify-center min-h-[300px]">
        <Activity className="animate-spin text-blue-600 mb-3" size={28} />
        <p className="text-slate-500 text-sm font-medium">Loading historical confidence timeline...</p>
      </div>
    );
  }

  if (!timeline || timeline.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
          <TrendingUp className="text-blue-600" size={22} />
          Confidence Timeline
        </h2>
        <p className="mt-4 text-slate-500 text-sm">No timeline events recorded yet.</p>
      </div>
    );
  }

  const chartData = timeline.map((item) => ({
    confidence: Number((item.confidence * 100).toFixed(1)),
    time: new Date(item.created_at).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
    reason: item.reason || item.evidence_type,
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h2 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
            <TrendingUp className="text-blue-600" size={22} />
            Confidence Timeline
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time multimodal confidence trajectory across the interview
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-medium">
          <span className="flex items-center gap-1.5 text-emerald-700">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> High / Increasing
          </span>
          <span className="flex items-center gap-1.5 text-amber-700">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Unstable
          </span>
          <span className="flex items-center gap-1.5 text-red-700">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> Dropping / Flagged
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#64748b" }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#64748b" }} />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const dataItem = payload[0].payload;
                return (
                  <div className="bg-slate-900 text-white text-xs rounded-lg p-3 shadow-lg border border-slate-700 max-w-xs">
                    <p className="font-semibold text-blue-400">{label}</p>
                    <p className="text-base font-bold my-1">{dataItem.confidence}% Confidence</p>
                    {dataItem.reason && (
                      <p className="text-slate-300 opacity-90">{dataItem.reason}</p>
                    )}
                  </div>
                );
              }
              return null;
            }}
          />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={(props) => <CustomColoredDot {...props} data={chartData} />}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
